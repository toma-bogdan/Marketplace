"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock
import logging
from logging.handlers import RotatingFileHandler
import unittest
from .product import Coffee

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.register_producer_lock = Lock() # lock used to register a producer
        self.new_cart_lock = Lock() # lock used to give a customer a new cart
        self.add_cart_lock = Lock() # lock used to remove safely a product from the product queue
        self.publish_lock = Lock()
        self.id_prod = 0 # represents the id of the last producer (it will be incremented by 1 every time a producer is created)
        self.id_cart = 0 # same as id_prod, but for consumer cart's
        self.consumer_carts = {} # dictionary that stores consumer carts by their id
        self.producer_sizes = {} # dictionary that stores the number of products each producer have by their id
        self.producers_ids = {} # dictionary that stores the producer id by their product
        self.products = [] # stores all the products

        self.logger = logging.getLogger("Marketplace")
        self.logger.setLevel(logging.INFO)
        self.handler = RotatingFileHandler("marketplace.log", maxBytes=1000000, backupCount=5)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.handler.doRollover()
        self.logger.addHandler(self.handler)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        with self.register_producer_lock:
            self.logger.info("A new producer will be registered")
            self.id_prod = self.id_prod + 1
            self.producer_sizes.__setitem__(self.id_prod, 0)
            self.logger.info('New producer registered with id %d', self.id_prod)

        return self.id_prod

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.logger.info('Producer %d publishing new product: %s', producer_id, product.__str__())

        with self.publish_lock:
            current_size = self.producer_sizes.get(producer_id)
            if current_size >= self.queue_size_per_producer:
                return False

            self.producer_sizes[producer_id] = current_size + 1
            self.products.append(product)
            self.producers_ids.__setitem__(product, producer_id)

        self.logger.info('Product published successfully by producer: %s, size of the \
        producer queue: %d', product, self.producer_sizes[producer_id])
        return True


    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.logger.info('Initializing a new cart')

        with self.new_cart_lock:
            self.id_cart = self.id_cart + 1
            self.consumer_carts.__setitem__(self.id_cart, [])
            self.logger.info('New cart created with id: %d', self.id_cart)

        return self.id_cart

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.logger.info('Trying to add product to the cart with id %s', cart_id)
        if product in self.products:
            with self.add_cart_lock:
                # Remove the product from the queue and decrement the producer size
                self.products.remove(product)
                self.producer_sizes[self.producers_ids[product]] -= 1

            # Adds the product in the consumer cart
            cart_items = self.consumer_carts.get(cart_id)
            cart_items.append(product)
            self.consumer_carts.__setitem__(cart_id, cart_items)

            self.logger.info('Successfully added product to the consumer cart')
            return True
        self.logger.info('The produs is not available')
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info('Removing product from cart')
        with self.add_cart_lock:
            self.producer_sizes[self.producers_ids[product]] += 1
            self.products.append(product)
        cart_items = self.consumer_carts.get(cart_id)
        cart_items.remove(product)
        self.consumer_carts.__setitem__(cart_id, cart_items)
        self.logger.info('Successfully removed product from cart: %s')

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        self.logger.info('Placing order for cart: %s', cart_id)
        cart_items = self.consumer_carts.get(cart_id)
        self.consumer_carts.__delitem__(cart_id)
        self.logger.info('Order placed successfully')
        return cart_items

class TestMarketplace(unittest.TestCase):
    """
        Test class for Marketplace
    """
    def setUp(self):
        self.marketplace = Marketplace(queue_size_per_producer=5)

    def test_register_producer(self):
        """
            Check register_producer method
        """
        producer_id = self.marketplace.register_producer()
        producer_id2 = self.marketplace.register_producer()
        self.assertEqual(producer_id, 1)
        self.assertEqual(producer_id2, 2)

    def test_publish(self):
        """
            Check publish method
        """
        producer_id = self.marketplace.register_producer()
        prod1 = {
            "product_type": "Coffee",
            "name": "Indonezia",
            "acidity": 5,
            "roast_level": "MEDIUM",
            "price": 1
        }.__str__()

        prod2 = {
            "product_type": "Coffee",
            "name": "Indonezia",
            "acidity": 5,
            "roast_level": "LOW",
            "price": 5
        }.__str__()

        success = self.marketplace.publish(producer_id, prod1)
        self.assertTrue(success)
        self.assertEqual(len(self.marketplace.products), 1)
        self.assertEqual(self.marketplace.producer_sizes[producer_id], 1)
        self.assertEqual(self.marketplace.producers_ids[prod1], producer_id)
        res = self.marketplace.publish(producer_id, prod2)
        self.assertTrue(res)

    def test_new_cart(self):
        """
            Check new cart method
        """
        cart_id = self.marketplace.new_cart()
        self.assertEqual(cart_id, 1)
        self.assertIn(cart_id, self.marketplace.consumer_carts)

    def test_multiple_carts(self):
        """
            Check new cart method with multiple carts
        """
        cart_id_1 = self.marketplace.new_cart()
        cart_id_2 = self.marketplace.new_cart()
        self.assertEqual(cart_id_1, 1)
        self.assertEqual(cart_id_2, 2)
        self.assertIn(cart_id_1, self.marketplace.consumer_carts)
        self.assertIn(cart_id_2, self.marketplace.consumer_carts)

    def test_add_to_cart(self):
        """
            Check add to cart method
        """
        product1 = Coffee(name="Indonezia", acidity="5", roast_level="MEDIUM", price=10)
        product2 = Coffee(name="Indonezia", acidity="10", roast_level="LOW", price=1)
        producer_id = self.marketplace.register_producer()
        self.marketplace.publish(producer_id, product1)
        self.marketplace.publish(producer_id, product2)
        cart_id = self.marketplace.new_cart()

        # Try adding product to the cart with id 1
        self.assertTrue(self.marketplace.add_to_cart(cart_id, product1))
        self.assertTrue(self.marketplace.add_to_cart(cart_id, product2))

    def test_remove_to_cart(self):
        """
            Check remove from cart
        """
        prod_id1 = self.marketplace.register_producer()
        product1 = Coffee(name="Indonezia", acidity="5", roast_level="MEDIUM", price=10)
        product2 = Coffee(name="Indonezia", acidity="10", roast_level="LOW", price=1)

        self.marketplace.publish(prod_id1, product1)
        self.marketplace.publish(prod_id1, product2)
        cart_id = self.marketplace.new_cart()

        self.marketplace.add_to_cart(cart_id, product1)
        self.marketplace.add_to_cart(cart_id, product2)

        self.marketplace.remove_from_cart(cart_id, product1)
        self.assertEqual(self.marketplace.producer_sizes[prod_id1], 1)

    def test_place_order(self):
        """
            Check place order method
        """
        prod_id1 = self.marketplace.register_producer()
        product1 = Coffee(name="Indonezia", acidity="5", roast_level="MEDIUM", price=10)
        product2 = Coffee(name="Indonezia", acidity="10", roast_level="LOW", price=1)

        self.marketplace.publish(prod_id1, product1)
        self.marketplace.publish(prod_id1, product2)
        cart_id = self.marketplace.new_cart()

        self.marketplace.add_to_cart(cart_id, product1)
        self.marketplace.add_to_cart(cart_id, product2)

        order_items = self.marketplace.place_order(cart_id)
        self.assertEqual(order_items, [product1, product2])
