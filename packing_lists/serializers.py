from rest_framework import serializers
from .models import School, Base, Store, PackingList, Item, PackingListItem, Price, Vote


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'address', 'latitude', 'longitude']


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = ['id', 'name', 'address', 'latitude', 'longitude']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'address_line1', 'address_line2', 'city', 'state',
            'zip_code', 'country', 'full_address_legacy', 'url', 'latitude',
            'longitude', 'is_online', 'is_in_person'
        ]


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description']


class PriceSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        source='store',
        write_only=True
    )

    class Meta:
        model = Price
        fields = ['id', 'item', 'store', 'store_id', 'price', 'quantity', 'date_purchased']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'price', 'is_correct_price', 'ip_address', 'created_at']


class PackingListItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
        source='item',
        write_only=True,
        required=False
    )
    item_name = serializers.CharField(write_only=True, required=False)
    item_description = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = PackingListItem
        fields = [
            'id', 'packing_list', 'item', 'item_id', 'item_name', 'item_description',
            'quantity', 'notes', 'packed', 'section', 'nsn_lin', 'required', 'instructions'
        ]

    def create(self, validated_data):
        # Handle creating new item if item_name is provided
        item_name = validated_data.pop('item_name', None)
        item_description = validated_data.pop('item_description', '')

        if item_name:
            item, created = Item.objects.get_or_create(
                name=item_name,
                defaults={'description': item_description}
            )
            validated_data['item'] = item

        return super().create(validated_data)


class PackingListSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    base = BaseSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        source='school',
        write_only=True,
        required=False,
        allow_null=True
    )
    base_id = serializers.PrimaryKeyRelatedField(
        queryset=Base.objects.all(),
        source='base',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PackingList
        fields = [
            'id', 'name', 'description', 'school', 'school_id', 'base', 'base_id',
            'type', 'custom_type'
        ]


class PriceWithVotesSerializer(serializers.Serializer):
    price = PriceSerializer()
    upvotes = serializers.IntegerField()
    downvotes = serializers.IntegerField()
    vote_confidence = serializers.FloatField()
    price_per_unit = serializers.FloatField()


class ItemWithPricesSerializer(serializers.Serializer):
    pli = PackingListItemSerializer()
    item = ItemSerializer()
    prices_with_votes = PriceWithVotesSerializer(many=True)


class PackingListDetailSerializer(serializers.Serializer):
    packing_list = PackingListSerializer()
    items_with_prices = ItemWithPricesSerializer(many=True)
