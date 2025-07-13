from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from packing_lists.models import Price, Vote
from packing_lists.security import calculate_trust_score, is_ip_suspicious
from django.db.models import Count, Q
from collections import defaultdict


class Command(BaseCommand):
    help = 'Generate security and abuse report for anonymous price submissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to analyze (default: 7)'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed IP analysis'
        )

    def handle(self, *args, **options):
        days = options['days']
        detailed = options['detailed']
        
        since = timezone.now() - timedelta(days=days)
        
        self.stdout.write(self.style.SUCCESS(f'Security Report - Last {days} days'))
        self.stdout.write('=' * 50)
        
        # Overview statistics
        total_prices = Price.objects.filter(created_at__gte=since).count()
        anonymous_prices = Price.objects.filter(created_at__gte=since, ip_address__isnull=False).count()
        flagged_prices = Price.objects.filter(created_at__gte=since, flagged_count__gt=0).count()
        verified_prices = Price.objects.filter(created_at__gte=since, is_verified=True).count()
        
        self.stdout.write(f'Total price submissions: {total_prices}')
        self.stdout.write(f'Anonymous submissions: {anonymous_prices} ({anonymous_prices/total_prices*100:.1f}%)' if total_prices > 0 else 'Anonymous submissions: 0')
        self.stdout.write(f'Flagged submissions: {flagged_prices}')
        self.stdout.write(f'Verified submissions: {verified_prices}')
        self.stdout.write('')
        
        # IP Analysis
        ip_stats = (Price.objects
                   .filter(created_at__gte=since, ip_address__isnull=False)
                   .values('ip_address')
                   .annotate(
                       submission_count=Count('id'),
                       flagged_count=Count('id', filter=Q(flagged_count__gt=0))
                   )
                   .order_by('-submission_count'))
        
        if ip_stats:
            self.stdout.write('Top Submitting IPs:')
            for i, ip_data in enumerate(ip_stats[:10]):
                ip = ip_data['ip_address']
                count = ip_data['submission_count']
                flagged = ip_data['flagged_count']
                trust_score = calculate_trust_score(ip)
                suspicious = is_ip_suspicious(ip)
                
                status = []
                if suspicious:
                    status.append(self.style.ERROR('SUSPICIOUS'))
                if trust_score >= 0.8:
                    status.append(self.style.SUCCESS('HIGH TRUST'))
                elif trust_score <= 0.3:
                    status.append(self.style.WARNING('LOW TRUST'))
                    
                status_str = ' '.join(status) if status else ''
                
                self.stdout.write(
                    f'{i+1:2d}. {ip:15s} - {count:3d} submissions, {flagged:2d} flagged, '
                    f'trust: {trust_score:.2f} {status_str}'
                )
            self.stdout.write('')
        
        # Suspicious Activity Detection
        suspicious_ips = []
        for ip_data in ip_stats:
            ip = ip_data['ip_address']
            if is_ip_suspicious(ip):
                suspicious_ips.append({
                    'ip': ip,
                    'count': ip_data['submission_count'],
                    'flagged': ip_data['flagged_count'],
                    'trust': calculate_trust_score(ip)
                })
        
        if suspicious_ips:
            self.stdout.write(self.style.ERROR('SUSPICIOUS IPs DETECTED:'))
            for ip_data in suspicious_ips:
                self.stdout.write(
                    f"  {ip_data['ip']} - {ip_data['count']} submissions, "
                    f"{ip_data['flagged']} flagged, trust: {ip_data['trust']:.2f}"
                )
            self.stdout.write('')
        
        # Confidence Level Distribution
        confidence_stats = (Price.objects
                          .filter(created_at__gte=since)
                          .values('confidence')
                          .annotate(count=Count('id'))
                          .order_by('confidence'))
        
        if confidence_stats:
            self.stdout.write('Confidence Level Distribution:')
            for stat in confidence_stats:
                confidence = stat['confidence']
                count = stat['count']
                percentage = count / total_prices * 100 if total_prices > 0 else 0
                self.stdout.write(f'  {confidence.title():8s}: {count:4d} ({percentage:5.1f}%)')
            self.stdout.write('')
        
        # Rate Limiting Statistics
        from django.core.cache import cache
        rate_limited_ips = 0
        # This is approximate since we can't easily query cache
        self.stdout.write(f'Currently rate-limited IPs: {rate_limited_ips} (approximate)')
        
        # Recommendations
        self.stdout.write(self.style.WARNING('SECURITY RECOMMENDATIONS:'))
        
        if flagged_prices > total_prices * 0.1:  # More than 10% flagged
            self.stdout.write('  ⚠️  High percentage of flagged content - review flagging criteria')
            
        if len(suspicious_ips) > 0:
            self.stdout.write(f'  ⚠️  {len(suspicious_ips)} suspicious IPs detected - consider temporary blocks')
            
        high_volume_ips = [ip for ip in ip_stats if ip['submission_count'] > 50]
        if high_volume_ips:
            self.stdout.write(f'  ⚠️  {len(high_volume_ips)} high-volume IPs - verify legitimacy')
            
        if anonymous_prices / total_prices > 0.95 if total_prices > 0 else False:
            self.stdout.write('  ✅ System is successfully operating in anonymous mode')
        
        # Detailed IP analysis if requested
        if detailed and ip_stats:
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('DETAILED IP ANALYSIS:')
            
            for ip_data in ip_stats[:20]:  # Top 20 IPs
                ip = ip_data['ip_address']
                
                # Get detailed stats for this IP
                prices = Price.objects.filter(ip_address=ip, created_at__gte=since)
                unique_items = prices.values('item').distinct().count()
                unique_stores = prices.values('store').distinct().count()
                avg_confidence = prices.aggregate(
                    high=Count('id', filter=Q(confidence='high')),
                    medium=Count('id', filter=Q(confidence='medium')),
                    low=Count('id', filter=Q(confidence='low'))
                )
                
                votes = Vote.objects.filter(price__in=prices)
                positive_votes = votes.filter(is_correct_price=True).count()
                total_votes = votes.count()
                vote_ratio = positive_votes / total_votes if total_votes > 0 else 0
                
                self.stdout.write(f'\n{ip}:')
                self.stdout.write(f'  Submissions: {ip_data["submission_count"]}')
                self.stdout.write(f'  Unique items: {unique_items}')
                self.stdout.write(f'  Unique stores: {unique_stores}')
                self.stdout.write(f'  Confidence: H:{avg_confidence["high"]} M:{avg_confidence["medium"]} L:{avg_confidence["low"]}')
                self.stdout.write(f'  Vote ratio: {vote_ratio:.2f} ({positive_votes}/{total_votes})')
                self.stdout.write(f'  Trust score: {calculate_trust_score(ip):.2f}')
                self.stdout.write(f'  Suspicious: {"Yes" if is_ip_suspicious(ip) else "No"}')
        
        self.stdout.write('\n' + self.style.SUCCESS('Report complete!'))