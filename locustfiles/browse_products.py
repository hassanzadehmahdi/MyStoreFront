from random import randint

from locust import task, HttpUser, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task(2)
    def view_products(self):
        print('view_products')
        collection_id = randint(2, 6)
        self.client.get(f'/store/products/?collection_id={collection_id}', name='/store/products')

    @task(4)
    def view_product_by_id(self):
        print('view_product_by_id')
        product_id = randint(10, 1000)
        self.client.get(f'/store/products/{product_id}', name='/store/products/:id')

    @task(1)
    def add_to_cart(self):
        print('add_to_cart')
        product_id = randint(10, 20)
        self.client.post(f'/store/carts/{self.cart_id}/items/',
                         name='/store/carts/items',
                         json={'product_id': product_id, 'quantity': 1})

    @task(1)
    def say_hello(self):
        print('say_hello')
        self.client.get('/playground/hello/', name='/playground/hello')

    def on_start(self):
        response = self.client.post('/store/carts/')
        result = response.json()
        self.cart_id = result['id']
