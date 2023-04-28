"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread, currentThread
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

    def run(self):
        for cart in self.carts:
            id_cart = self.marketplace.new_cart()
            for action in cart:
                action_type = action['type']
                action_product = action['product']
                action_quantity = action['quantity']

                for _ in range(action_quantity):
                    if action_type == "add":
                        res = self.marketplace.add_to_cart(id_cart, action_product)
                        while res is False:
                            time.sleep(self.retry_wait_time)
                            res = self.marketplace.add_to_cart(id_cart, action_product)
                    elif action_type == "remove":
                        self.marketplace.remove_from_cart(id_cart, action_product)

            # Place the order and print the items and who bought them
            cart_items = self.marketplace.place_order(id_cart)
            for item in cart_items:
                print("{} bought {}".format(currentThread().getName(), item))
