from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, F
from decimal import Decimal

from .models import School, Base, Store, PackingList, Item, PackingListItem, Price, Vote
from .serializers import (
    SchoolSerializer, BaseSerializer, StoreSerializer, PackingListSerializer,
    ItemSerializer, PackingListItemSerializer, PriceSerializer, VoteSerializer,
    PackingListDetailSerializer
)


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class BaseViewSet(viewsets.ModelViewSet):
    queryset = Base.objects.all()
    serializer_class = BaseSerializer


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class PackingListViewSet(viewsets.ModelViewSet):
    queryset = PackingList.objects.all().select_related('school', 'base')
    serializer_class = PackingListSerializer

    @action(detail=True, methods=['get'])
    def detail_view(self, request, pk=None):
        """Get detailed packing list with all items and prices"""
        packing_list = self.get_object()

        # Get all items for this packing list
        packing_list_items = PackingListItem.objects.filter(
            packing_list=packing_list
        ).select_related('item').prefetch_related('item__prices__store', 'item__prices__votes')

        items_with_prices = []
        for pli in packing_list_items:
            # Get all prices for this item
            prices = Price.objects.filter(item=pli.item).select_related('store').prefetch_related('votes')

            prices_with_votes = []
            for price in prices:
                upvotes = price.votes.filter(is_correct_price=True).count()
                downvotes = price.votes.filter(is_correct_price=False).count()
                total_votes = upvotes + downvotes
                vote_confidence = (upvotes - downvotes) / max(total_votes, 1)
                price_per_unit = float(price.price) / price.quantity if price.quantity > 0 else 0

                prices_with_votes.append({
                    'price': PriceSerializer(price).data,
                    'upvotes': upvotes,
                    'downvotes': downvotes,
                    'vote_confidence': vote_confidence,
                    'price_per_unit': price_per_unit,
                })

            # Sort by vote confidence then price per unit
            prices_with_votes.sort(key=lambda x: (-x['vote_confidence'], x['price_per_unit']))

            items_with_prices.append({
                'pli': PackingListItemSerializer(pli).data,
                'item': ItemSerializer(pli.item).data,
                'prices_with_votes': prices_with_votes,
            })

        response_data = {
            'packing_list': PackingListSerializer(packing_list).data,
            'items_with_prices': items_with_prices,
        }

        return Response(response_data)

    @action(detail=True, methods=['post'])
    def toggle_packed(self, request, pk=None):
        """Toggle packed status for an item"""
        item_id = request.data.get('toggle_packed_item_id')
        if not item_id:
            return Response(
                {'error': 'toggle_packed_item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pli = PackingListItem.objects.get(id=item_id, packing_list_id=pk)
            pli.packed = not pli.packed
            pli.save()
            return Response({'success': True, 'packed': pli.packed})
        except PackingListItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class PackingListItemViewSet(viewsets.ModelViewSet):
    queryset = PackingListItem.objects.all().select_related('item', 'packing_list')
    serializer_class = PackingListItemSerializer


class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all().select_related('item', 'store')
    serializer_class = PriceSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    def create(self, request, *args, **kwargs):
        """Create a vote for a price"""
        price_id = request.data.get('price_id')
        is_upvote = 'upvote_price_id' in request.data

        if not price_id:
            return Response(
                {'error': 'price_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            price = Price.objects.get(id=price_id)
        except Price.DoesNotExist:
            return Response(
                {'error': 'Price not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get IP address
        ip_address = self.get_client_ip(request)

        # Create vote
        vote = Vote.objects.create(
            price=price,
            is_correct_price=is_upvote,
            ip_address=ip_address
        )

        serializer = self.get_serializer(vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
