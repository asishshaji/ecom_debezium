from enum import Enum


class Action(Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    SCROLL = "SCROLL"
    CLICK_PRODUCT = "CLICK_PRODUCT"
    ADD_TO_CART = "ADD_TO_CART"
    PURCHASE = "PURCHASE"
    CANCEL = "CANCEL"
