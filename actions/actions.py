from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, FollowupAction

from .backend import get_products, get_stock, get_orders

def _normalize_text(value: str) -> str:
    return value.strip().lower()

def _normalize_category(value: Optional[str]) -> Optional[str]:
    if not value:
        return value

    value = value.strip().lower()

    aliases = {
        "topánky": "shoes",
        "topanky": "shoes",
        "tenisky": "shoes",
        "boty": "shoes",
        "shoes": "shoes",

        "doplnky": "supplements",
        "doplnky výživy": "supplements",
        "doplnky vyzivy": "supplements",
        "proteíny": "supplements",
        "proteiny": "supplements",
        "suplementy": "supplements",
        "supplements": "supplements",

        "elektronika": "electronics",
        "electronics": "electronics",

        "phone": "phones",
        "phones": "phones",
        "telefóny": "phones",
        "telefony": "phones",
        "mobily": "phones",
        "mobily": "phones",
    }

    return aliases.get(value, value)

def _find_product(products: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    if not name:
        return None

    name_low = _normalize_text(name)

    for p in products:
        if _normalize_text(p.get("name", "")) == name_low:
            return p

    for p in products:
        if name_low in _normalize_text(p.get("name", "")):
            return p

    words = [w for w in name_low.split() if len(w) > 2]
    if words:
        for p in products:
            product_name = _normalize_text(p.get("name", ""))
            if all(word in product_name for word in words):
                return p

    return None

def _get_stock_for_product(product_id: str, stock_data: List[Dict[str, Any]]) -> int:
    item = next((s for s in stock_data if s.get("product_id") == product_id), None)
    return int(item.get("stock", 0)) if item else 0

class ActionRouteCheckStock(Action):
    def name(self) -> Text:
        return "action_route_check_stock"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get("entities", []) or []
        has_product_entity = any(e.get("entity") == "product_name" for e in entities)

        if has_product_entity:
            return [
                SlotSet("candidate_product_name", None),
                SlotSet("confirm_product", None),
                FollowupAction("stock_form"),
            ]

        last_product = tracker.get_slot("product_name")

        if last_product:
            dispatcher.utter_message(
                response="utter_confirm_product_for_stock",
                candidate_product_name=last_product,
            )
            return [
                SlotSet("candidate_product_name", last_product),
                SlotSet("confirm_product", None),
            ]

        return [FollowupAction("stock_form")]


class ActionSetCandidateAsProduct(Action):
    def name(self) -> Text:
        return "action_set_candidate_as_product"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        cand = tracker.get_slot("candidate_product_name")
        if cand:
            return [SlotSet("product_name", cand)]
        return []


class ActionClearCandidate(Action):
    def name(self) -> Text:
        return "action_clear_candidate"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("candidate_product_name", None),
            SlotSet("confirm_product", None),
        ]

class ActionSearchProduct(Action):
    def name(self) -> Text:
        return "action_search_product"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        products = get_products()

        latest_entities = tracker.latest_message.get("entities", []) or []

        latest_product = None
        latest_category = None

        raw_text = (tracker.latest_message.get("text") or "").strip().lower()

        for e in latest_entities:
            if e.get("entity") == "product_name" and e.get("value"):
                latest_product = e.get("value")
            if e.get("entity") == "category" and e.get("value"):
                latest_category = e.get("value")

        product_name = latest_product if latest_product else tracker.get_slot("product_name")
        category = latest_category if latest_category else tracker.get_slot("category")
        category = _normalize_category(category)

        if latest_category and not latest_product:
            cat = _normalize_category(latest_category)
            results = [p for p in products if p.get("category", "").lower() == cat]

            if not results:
                dispatcher.utter_message(
                    text=f"V kategórii „{latest_category}“ som nenašiel žiadne produkty."
                )
                return [SlotSet("category", latest_category), SlotSet("product_name", None)]

            lines = [f"- {p['name']} ({p['category']}), {p['price']} €" for p in results[:5]]
            dispatcher.utter_message(text="Tu je niekoľko produktov z ponuky:\n" + "\n".join(lines))
            return [SlotSet("category", latest_category), SlotSet("product_name", None)]

        known_categories = {p.get("category", "").lower() for p in products if p.get("category")}
        if raw_text in known_categories:
            results = [p for p in products if p.get("category", "").lower() == raw_text]
            if results:
                lines = [f"- {p['name']} ({p['category']}), {p['price']} €" for p in results[:5]]
                dispatcher.utter_message(text="Našiel som napríklad tieto produkty:\n" + "\n".join(lines))
                return [SlotSet("category", raw_text), SlotSet("product_name", None)]
        
        if product_name:
            p = _find_product(products, product_name)
            if p:
                dispatcher.utter_message(
                    text=f"Našiel som tieto produkty:\n- {p['name']} ({p['category']}), {p['price']} €"
                )
                return [SlotSet("product_name", p["name"])]
            else:
                dispatcher.utter_message(
                    text=f"Produkt „{product_name}“ som nenašiel. Skús presnejší názov alebo inú kategóriu."
                )
                return [SlotSet("product_name", None)]

        if category:
            cat = _normalize_category(category)
            results = [p for p in products if p.get("category", "").lower() == cat]

            if not results:
                dispatcher.utter_message(
                    text=f"V kategórii „{category}“ som nenašiel žiadne produkty."
                )
                return []

            lines = [f"- {p['name']} ({p['category']}), {p['price']} €" for p in results[:5]]
            dispatcher.utter_message(text="Našiel som tieto produkty:\n" + "\n".join(lines))
            return [SlotSet("product_name", None)]

        dispatcher.utter_message(
            text="Napíš názov produktu alebo kategóriu, napríklad Nike Air Max alebo topánky."
        )
        return []

class ActionListProducts(Action):
    def name(self) -> Text:
        return "action_list_products"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        products = get_products()

        if not products:
            dispatcher.utter_message(text="Momentálne nemám k dispozícii žiadne produkty.")
            return []

        lines = []
        for p in products[:10]:
            name = p.get("name", "Neznámy produkt")
            category = p.get("category", "bez kategórie")
            price = p.get("price", 0)
            lines.append(f"- {name} ({category}), {price} €")

        dispatcher.utter_message(
            text="Momentálne mám v ponuke napríklad tieto produkty:\n" + "\n".join(lines)
        )
        return []
    
class ActionListInStockProducts(Action):
    def name(self) -> Text:
        return "action_list_in_stock_products"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        products = get_products()
        stock = get_stock()

        available = []
        for p in products:
            qty = _get_stock_for_product(p["id"], stock)
            if qty > 0:
                available.append((p, qty))

        if not available:
            dispatcher.utter_message(text="Momentálne nemám žiadne produkty na sklade.")
            return []

        lines = []
        for p, qty in available[:10]:
            lines.append(f"- {p['name']} ({p['category']}), {qty} ks")

        dispatcher.utter_message(
            text="Momentálne sú na sklade napríklad tieto produkty:\n" + "\n".join(lines)
        )
        return []
    
class ActionCheckStock(Action):
    def name(self) -> Text:
        return "action_check_stock"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        products = get_products()
        stock = get_stock()

        product_name = tracker.get_slot("product_name")
        if not product_name:
            dispatcher.utter_message(response="utter_ask_product_name")
            return []

        p = _find_product(products, product_name)
        if not p:
            dispatcher.utter_message(
                text=f"Produkt „{product_name}“ som nenašiel v ponuke. Skús presnejší názov."
            )
            return [SlotSet("product_name", None)]

        qty = _get_stock_for_product(p["id"], stock)

        if qty > 0:
            dispatcher.utter_message(text=f"{p['name']} je na sklade. Počet kusov: {qty}.")
        else:
            dispatcher.utter_message(text=f"{p['name']} momentálne nie je na sklade.")

        return [SlotSet("product_name", p["name"])]


class ActionGetOrderStatus(Action):
    def name(self) -> Text:
        return "action_get_order_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        orders = get_orders()
        latest_entities = tracker.latest_message.get("entities", []) or []

        latest_order_id = None
        for e in latest_entities:
            if e.get("entity") == "order_id" and e.get("value"):
                latest_order_id = e.get("value")

        order_id = latest_order_id if latest_order_id else tracker.get_slot("order_id")

        if not latest_order_id:
            dispatcher.utter_message(response="utter_ask_order_id")
            return [SlotSet("order_id", None)]

        if not order_id:
            dispatcher.utter_message(response="utter_ask_order_id")
            return []

        oid = order_id.strip().upper()
        order = next((o for o in orders if o.get("order_id", "").upper() == oid), None)

        if not order:
            dispatcher.utter_message(text=f"Nenašiel som objednávku {oid}. Skontroluj číslo objednávky.")
            return []

        status = order.get("status", "unknown")
        dispatcher.utter_message(text=f"Stav objednávky {oid} je: {status}.")
        return [SlotSet("order_id", oid)]

class ValidateStockForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_stock_form"

    def validate_product_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value or not str(slot_value).strip():
            return {"product_name": None}

        return {"product_name": str(slot_value).strip()}


class ValidateOrderStatusForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_order_status_form"

    def validate_order_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value or not str(slot_value).strip():
            dispatcher.utter_message(text="Prosím napíš číslo objednávky (napr. ORD1002).")
            return {"order_id": None}

        return {"order_id": str(slot_value).strip().upper()}

class ActionAddToCart(Action):
    def name(self) -> Text:
        return "action_add_to_cart"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        products = get_products()
        stock = get_stock()

        product_name = tracker.get_slot("product_name")

        if not product_name:
            dispatcher.utter_message(response="utter_ask_product_name")
            return []

        p = _find_product(products, product_name)
        if not p:
            dispatcher.utter_message(
                text=f"Produkt „{product_name}“ ponuke nevidím. Skús presnejší názov."
            )
            return [SlotSet("product_name", None)]

        qty_available = _get_stock_for_product(p["id"], stock)
        if qty_available <= 0:
            dispatcher.utter_message(
                text=f"{p['name']} momentálne nie je na sklade, takže ho neviem pridať do košíka."
            )
            return [SlotSet("product_name", p["name"])]

        cart = tracker.get_slot("cart") or []

        for item in cart:
            if item.get("product_id") == p["id"]:
                item["qty"] = int(item.get("qty", 1)) + 1
                dispatcher.utter_message(
                    text=f"V košíku som zvýšil množstvo produktu {p['name']} na {item['qty']} ks."
                )
                return [SlotSet("cart", cart), SlotSet("product_name", p["name"])]

        cart.append(
            {
                "product_id": p["id"],
                "name": p["name"],
                "qty": 1,
                "price": p["price"],
            }
        )
        dispatcher.utter_message(text=f"Produkt {p['name']} som pridal do košíka.")
        return [SlotSet("cart", cart), SlotSet("product_name", p["name"])]


class ActionRemoveFromCart(Action):
    def name(self) -> Text:
        return "action_remove_from_cart"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("product_name")
        cart = tracker.get_slot("cart") or []

        if not cart:
            dispatcher.utter_message(text="Košík je prázdny.")
            return []

        if not product_name:
            dispatcher.utter_message(text="Ktorý produkt chceš odstrániť? Napíš jeho názov.")
            return []

        name_low = _normalize_text(product_name)
        new_cart = [item for item in cart if _normalize_text(item.get("name", "")) != name_low]

        if len(new_cart) == len(cart):
            dispatcher.utter_message(text=f"Produkt „{product_name}“ v košíku nevidím.")
            return []

        dispatcher.utter_message(text=f" Odstránil som {product_name} z košíka.")
        return [SlotSet("cart", new_cart)]


class ActionShowCart(Action):
    def name(self) -> Text:
        return "action_show_cart"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        cart = tracker.get_slot("cart") or []

        if not cart:
            dispatcher.utter_message(text="Košík je prázdny.")
            return []

        total = 0.0
        lines = []

        for item in cart:
            subtotal = float(item["price"]) * int(item["qty"])
            total += subtotal
            lines.append(f"- {item['name']} x{item['qty']} = {subtotal:.2f} €")

        dispatcher.utter_message(
            text="Tvoj košík:\n" + "\n".join(lines) + f"\nSpolu: {total:.2f} €"
        )
        return []


class ActionClearCart(Action):
    def name(self) -> Text:
        return "action_clear_cart"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        cart = tracker.get_slot("cart") or []

        if not cart:
            dispatcher.utter_message(text="Košík je už prázdny.")
            return []

        dispatcher.utter_message(response="utter_cart_cleared")
        return [SlotSet("cart", [])]


class ActionResetProductName(Action):
    def name(self) -> Text:
        return "action_reset_product_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("product_name", None)]


class ActionResetOrderId(Action):
    def name(self) -> Text:
        return "action_reset_order_id"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("order_id", None)]