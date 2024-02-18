# aiogram-ui

Tools to easily create ui(buttons, messages, etc..) for telegram bots powered by aiogram

## Content

- [aiogram-ui](#aiogram-ui)
  - [Content](#content)
  - [Inline Keyboards](#inline-keyboards)
    - [Basic usage](#basic-usage)
    - [Making button](#making-button)
    - [Callback button](#callback-button)
    - [Button actions](#button-actions)
    - [Making keyboard](#making-keyboard)
    - [Concatenating keyboards](#concatenating-keyboards)
    - [Removing line from keyboard](#removing-line-from-keyboard)
  - [Callbacks](#callbacks)
    - [CallbackData](#callbackdata)
    - [FilterableStr](#filterablestr)
  - [Deep Links](#deep-links)

## Inline Keyboards

### Basic usage

```python
from aiogram_ui import KB, B, OpenURL


kb = KB(
    B(
        "Open url", OpenURL("https://google.com")
    ),  # There are also other types of actions (OpenWebApp and ShareText)
    B(
        "Some callback data", "my_cb_data"
    ),  # If the string is passed as second argument, it will be used as callback_data
)
```

### Making button

```python
B(
    text: str, 
    action: Union[str, CallbackData, BAction], 
    show: bool = True
):
    """
    arguments:
    :text: - The text to display on button
    :action: - The action to perform, can be a string, BAction or a CallbackData
    :show: - Whether to show the button

    :return: IKB(InlineKeyboardButton with some features) object if show is True, otherwise None
    """
    ...
```

Is used to create buttons in the keyboard of different types (url, callback_data, WebApp).

### Callback button

You can pass a callback data as string or as ```CallbackData``` object to ```B``` function.

```python
from aiogram_ui import B, CallbackData

# aiogram_ui.CallbackData is the same as original aiogram.filters.callback_data.CallbackData but with support for datetime fields

class PageCD(CallbackData, prefix="page"):
    page: int

```

### Button actions

Button actions are all subclasses of ```BAction```, and can be passed as action argument.

```python
class OpenURL(BAction):
    """A class that represents an open URL action."""
    def __init__(self, url: str):
        """
        :url: - The URL to open
        """
        ...

class OpenWebApp(BAction):
    """A class that represents an open Web App action."""
    def __init__(self, url: str):
        """
        :url: - The URL of WebApp to open
        """
        ...

class ShareText(OpenURL):
    """A class that represents a share text action."""
    def __init__(self, url: str, text: Optional[str] = None):
        """
        "url: - The URL to share
        "text: - The text to share
        see more: https://core.telegram.org/widgets/share
        """

```

### Making keyboard

```aiogram-ui``` provides a way to create ```InlineKeyboardMarkup``` using ```KB``` function. You can pass buttons in different ways.

```python
from aiogram_ui import KB

b1 = B("Callback", "callback_data")
b2 = B("Url", OpenURL("https://google.com"))
b3 = B("WebApp", OpenWebApp("https://google.com"), show=False) # This button will not be shown
b4 = B("Share", ShareText("https://google.com", "text"))

# 1. Just pass buttons to KB
kb1 = KB(b1, b2, b3, b4)

# 2. Pass a list of buttons (they will be interpreted as a line)
kb2 = KB([b1, b2, b3, b4])

# 3. Another InlineKeyboardMarkup
kb3 = KB((b1, b2), kb2)
```

You can combine different ways and it will work.

```KB``` has one key-word argument: ```vertical: bool = True```. So by default it will create a vertical layout keyboard. This means that each button passed as argument will be on a new line. This affects only arguments that are passed just as buttons.

### Concatenating keyboards

```python
cancel_button = B("Cancel", 'cancel')
menu_kb = KB(B('Our channel', OpenURL("https://t.me/...")), cancel_button)

"""You can concatenate keyboard with button. 

It will be interpreted as new line and will be added to the end of the keyboard."""
kb = KB(...) + cancel_button

"""Or you can concatenate keyboards"""
kb = KB(...) + menu_kb
```

### Removing line from keyboard

It could be useful in some cases, but very very rarely. Maybe not needed at all.

```python
new_kb = kb.without_line(1) # This will return a new keyboard without second line in it
```

## Callbacks

### CallbackData

This is very powerful [tool from aiogram](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/callback_data.html) but can also include datetime fields.

You can use it in ```B``` function as well. It will be automatically packed.

```python
class PageCD(CallbackData, prefix="page"):
    page: int


kb = KB(
    B("To page 1", PageCD(page=1)),
    B("To page 2", PageCD(page=2)),
)
```

### FilterableStr

It was made to use in callbacks Enums.
It is both a string and a callback_data filter.

For example,

```python
from enum import Enum
from aiogram_ui import CallbackData, FilterableStr
...

class DefaultCallbacks(FilterableStr, Enum):
    home = "home"
    cancel = "cancel"
    buy_me_a_beer = "buy_a_beer"

...

# Two handlers below have exactly the same behaviour
@router.callback_query(DefaultCallbacks.home)
async def home_handler(callback_query: types.CallbackQuery):
    ...

@router.callback_query(F.data == DefaultCallbacks.home)
async def home_handler(callback_query: types.CallbackQuery):
    ...
```

Why we need FilterableStr and Enum?

First of all, it is good idea to use Enums and not just strings as callback_data, as enums are linted so it will be harder to make a typo.

Secondly, FilterableStr provides a way to use less code writing filters for callback buttons.

## Deep Links

Filtering deep-links is very missing piece in aiogram

Thats why I've created class ```DeepLink``` that is very familirar with ```CallbackData```.

Example of using ```DeepLink```:

```python
from aiogram_ui import DeepLink

class ReferalDL(DeepLink, prefix="ref"):
    # By default it is encoded with url-safe base64. But you can set is_plain=True to use plain string.
    from_tg_id: int

@router.message(ReferalDL.filter(*optional magic_filter here*))
async def referal_link_handler(message: types.Message, deep_link: ReferalDL, bot: Bot):
    await message.answer(f"Yooo, {deep_link.from_tg_id} just invited you!")

    # To pack deep-link in url you can use:
    bot_me = await bot.me()
    url = ReferalDL(
        from_tg_id=message.from_user.id
    ).get_link(bot_me.username)

    await message.answer(f"Your invite deep-link is {url}")
```
