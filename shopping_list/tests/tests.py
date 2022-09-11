import pytest

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shopping_list.models import ShoppingList, ShoppingItem


@pytest.mark.django_db
def test_valid_shopping_list_is_created(create_user, create_authenticated_client):
    url = reverse("all-shopping-lists")
    data = {
        "name": "Groceries",
    }
    client = create_authenticated_client(create_user())
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.get().name == "Groceries"

@pytest.mark.django_db
def test_shopping_list_name_missing_returns_bad_request(create_user, create_authenticated_client):
    user = create_user()
    url = reverse("all-shopping-lists")
    data = {
        "stuff": "hello"
    }
    client = create_authenticated_client(user)
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_all_shopping_lists_are_listed(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)

    url = reverse("all-shopping-lists")
    create_shopping_list(name="Groceries", user=user)
    create_shopping_list(name="Books", user=user)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['name'] == "Groceries"
    assert response.data[1]['name'] == "Books"

@pytest.mark.django_db
def test_shopping_list_is_retrieved_by_id(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = create_authenticated_client(user)

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"

@pytest.mark.django_db
def test_shopping_list_includes_only_corresponding_items(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)
    another_shopping_list = create_shopping_list(name="Books", user=user)

    ShoppingItem.objects.create(shopping_list=shopping_list, name="Eggs", purchased=False)
    ShoppingItem.objects.create(shopping_list=another_shopping_list, name="Oher", purchased=False)

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = create_authenticated_client(user)
    response = client.get(url)

    assert len(response.data["shopping_items"]) == 1
    assert response.data["shopping_items"][0]["name"] == "Eggs"

@pytest.mark.django_db
def test_shopping_list_name_is_changed(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    
    data = {
        "name": "Food",
    }

    client = create_authenticated_client(user)
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"

@pytest.mark.django_db
def test_shopping_list_not_changed_because_name_missing(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "stuff": "stuff"
    }

    client = create_authenticated_client(user)
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_shopping_list_name_is_change_with_partial_update(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)
    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "name": "Food",
    }

    client = create_authenticated_client(user)
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"

@pytest.mark.django_db
def test_partial_update_with_missing_name_has_no_impact(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "stuff": "stuff"
    }

    client = create_authenticated_client(user)
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_shopping_list_is_deleted(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    client = create_authenticated_client(user)
    response =client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingList.objects.all()) == 0

@pytest.mark.django_db
def test_valid_shopping_item_is_created(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)
    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "Milk",
        "purchased": False
    }
    client = create_authenticated_client(user)
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_shopping_item_missing_data_returns_bad_request(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)
    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "Milk",
    }
    client = create_authenticated_client(user)
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_shopping_item_is_retrieved_by_id(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = create_authenticated_client(user)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Chocolate"

@pytest.mark.django_db
def test_change_shopping_item_purchased_status(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = create_authenticated_client(user)

    data = {
        "name": "Chocolate",
        "purchased": True
    }
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_missing_data_returns_bad_request(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = create_authenticated_client(user)

    data = {
        "purchased": True
    }
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_partial_update(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = create_authenticated_client(user)

    data = {
        "purchased": True
    }
    response = client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True

@pytest.mark.django_db
def test_shopping_item_is_deleted(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    client = create_authenticated_client(user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingItem.objects.all()) == 0

@pytest.mark.django_db
def test_update_shopping_list_restricted_if_not_member(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    shopping_list_creator = User.objects.create_user("Creator", "creator@list.com","something")
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(name="Groceries", user=shopping_list_creator)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "name": "Food",
    }

    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_partial_update_shopping_list_restricted_if_nnot_member(create_user, create_authenticated_client, create_shopping_list):
    user =  create_user()
    shopping_list_creator = User.objects.create_user("Creator", "creator@list.com","something")
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(name="Groceries", user=shopping_list_creator)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "name": "Food",
    }

    response = client.patch(url, data=data, format="json")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_admin_can_retrieve_shopping_list(create_user, create_shopping_list, admin_client):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    response = admin_client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_not_member_of_list_can_not_add_shopping_item(create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)

    shopping_list_creator = User.objects.create_user("Creator", "creator@list.com", "something")
    shopping_list = create_shopping_list(name="Groceries", user=shopping_list_creator)

    url = reverse("add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "milk",
        "purchased": False
    }

    response = client.post(url, data=data, format="json")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_admin_can_add_shopping_items(create_user, create_shopping_list, admin_client):
    user = create_user()
    shopping_list = create_shopping_list(name="Groceries", user=user)

    url = reverse("add-shopping-item", kwargs={"pk": shopping_list.id})

    data = {
        "name": "Milk",
        "purchased": False
    }

    response = admin_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_shopping_item_detail_access_restricted_if_not_member_of_shopping_list(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_list_creator = User.objects.create_user("Creator", "creator@list.com", "something")
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=shopping_list_creator)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_shopping_item_update_restricted_if_not_member_of_shopping_list(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_list_creator = User.objects.create_user("Creator", "creator@list.com", "something")
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=shopping_list_creator)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    data = {
        "name": "Chocolate",
        "purchased": True
    }

    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_shopping_item_partial_update_restricted_if_not_member_of_shopping_list(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_list_creator = User.objects.create_user("Creator", "creator@list.com", "something")
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=shopping_list_creator)

    url = reverse("shopping-item-detail",
                  kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    data = {
        "purchased": True
    }

    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_shopping_item_delete_restricted_if_not_member_of_shopping_list(create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    shopping_list_creator = User.objects.create_user("Creator", "creator@list.com", "something")
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=shopping_list_creator)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_admin_can_retrieve_single_shopping_item(create_user, create_shopping_item, admin_client):
    user = create_user()
    shopping_item = create_shopping_item("Milk", user)

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    response = admin_client.get(url)

    assert response.status_code == status.HTTP_200_OK
