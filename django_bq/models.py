from django.db import models
import logging

logger = logging.getLogger("django.db.models")

class BaseBigQueryModel(models.Model):
    """
    Base model for BigQuery with custom methods.
    """
    bq_primary_keys = []
    connection = 'bigquery'

    class Meta:
        abstract = True
        managed = False  # This model is managed by BigQuery, not Django migrations

    def save(self, *args, **kwargs):
        """
        Override save method to use BigQuery.
        """
        logger.debug('entering save')
        connection = kwargs.get('using')
        if not connection:
            logger.info('using default connection from the model')
            connection = self.connection
        logger.info(f"using connection {connection}")
        logger.info('to use a different connection, pass the connection name in the save method: save(using="<connection name>")')
        logger.debug('checking if primary key already exists in table')



        query_params =  {field.name: getattr(self, field.name) for field in self._meta.fields}


        if self.bq_primary_keys:
            logger.info('custom primary keys provided')
            logger.info(self.bq_primary_keys)
            filter_params = {key: getattr(self, key) for key in self.bq_primary_keys}
        else:
            logger.info('no custom primary keys provided, using primary key declared in model')
            filter_params = {'pk': self.pk}


        if not bool(self.__class__.objects.using(connection).filter(**filter_params)):
            logger.info('primary key does not exist, inserting new record')
            # If the instance does not have a primary key, insert it
            self.__class__.objects.using(connection).bulk_create([self])
        else:
            logger.info('primary key exists, updating existing record')
            # If the instance has a primary key, update it
            self.__class__.objects.using(connection).filter(**filter_params).update(**query_params)
