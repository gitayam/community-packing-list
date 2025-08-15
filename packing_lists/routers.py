"""
Database router for read/write splitting with PostgreSQL read replicas.
Routes read-only queries to read replica when available.
"""

from django.conf import settings

class DatabaseRouter:
    """
    A router to control all database operations on models
    """
    
    def db_for_read(self, model, **hints):
        """Reading from the read replica database."""
        # Use read replica for read operations if available
        if 'read_replica' in settings.DATABASES:
            return 'read_replica'
        return 'default'

    def db_for_write(self, model, **hints):
        """Writing to the primary database."""
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Relations between objects are allowed."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that migrations only run on the primary database."""
        return db == 'default'