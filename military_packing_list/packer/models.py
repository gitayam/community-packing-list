from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    reputation_score = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Price(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    store_name = models.CharField(max_length=255)
    submitted_by_name = models.CharField(max_length=100, default="Anonymous")
    submitted_at = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.item.name} - {self.price} at {self.store_name}"
