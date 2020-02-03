# vk_bot
simple bot on Python. 

### How to use:

### Install

```
$ git clone https://github.com/Ruthercode/vk_bot.git
$ cd vk_bot
```
### Usage
**Auto likes**:
At first, you must have token VK

example of token: **5277d48df2317b0597d43fa36fb0b694bc50f6496a516cb4f62ec4e26098a4efd157a155b01230cc46635**.


Put this in variable `token` in file `autolike.py`

At second, choose some users and enter their **id** in variable targets

At last, choose album, 3 album is available:
* `wall`;
* `profile`;
* `saved`.

example:
```python
album = "saved"
```
**Run**

```
python3 autolike.py
```

**Longpool mode:**

**Run**

```
python3 main.py
```

After run, send text messages for bot