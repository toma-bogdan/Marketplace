// Toma Bogdan-Nicolae
// 333CB

/*

            Multiple producer multiple consumer problem
    
        Producer:
    The producer creates the products given in the input file in an infinite loop. Every product
has a quantity and a certain wait_time, so the producer has to make x products, and wait y
seconds after each product. If the producer reaches maximum capacity, it waits republish_wait_time
seconds, then it tries again to publish the product.

        Consumer:
    The consumer gets a number of carts (mostly only one) with certain operation (Add or remove
products), with a given quantity for each. The thread calls add_cart or remove_from_Cart methods
from market place and if the product is unavailable, it sleeps retry_wait_time seconds. After
every operation is completed, the consumer places the order and prints the products.

        Market Place:

    Market place connects the producer and the consumer and offers the producers a queue_size_per_prod
which is the maximum capacity a producer can produce. Every producer and every cart of a consumer has
an id which is genereted by incrementing by 1 a variable every time a new producer/consumer is created.
Each time a producer/consumer(cart) is created a lock is used in order to not have any race condition.
    When producers publish a product the marketplace stores in an array every product, in a dictionary the
number of products each producer have (to not overcome the maximum capacity) and a dictionary that stores 
every product, their producer_id. Also, in the publish function we use a lock for incrementing safely the
producer_size.

    The add to cart function checks in the products list if the product is available. If not, return false,
else removes the product from the list, decrements the size and puts it in the cart_items dictionary with
cart_id and a list with all the products in the cart.

    The remove from cart, adds the product back to the list and increments the size of the producer items.
    Place order returns all the products in the cart, and delete the cart from the dictionary.

*/