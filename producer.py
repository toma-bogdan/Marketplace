"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.producer_id = marketplace.register_producer()


    def run(self):
        while True:
            for product in self.products:
                prod = product[0]
                quantity = product[1]
                wait_time = product[2]

                # Publish the products by their given quantity
                for _ in range(quantity):
                    res = self.marketplace.publish(self.producer_id, prod)
                    if res:
                        time.sleep(wait_time)
                    else:
                        # Wait until there is space in the queue
                        while res is False:
                            time.sleep(self.republish_wait_time)
                            res = self.marketplace.publish(self.producer_id, prod)
                        