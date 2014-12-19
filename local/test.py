from GoogleAPI import CSE

cse = CSE('AIzaSyAHb_rXVoAVdJq3fTuyQpU5scxF29BA2Tc', 
'009672557423963828148:mzxgb9ok-ts', 
'symphony x', None)

with open('sampleP1.json') as f:
    page1 = f.read()
with open('sampleP2.json') as f:
    page2 = f.read()

cse._test_feed = page1

page = cse.next()
print(page.title)

print(cse.pages.title)

print(cse.pages.current.items.current.title)
print(cse.pages.current.items.title)
page = cse.pages.current
items = page.items
items.next()

print(cse.pages.current.items.title)
items.next()
print(cse.pages.current.items.title)
items.next()
print(cse.pages.current.items.title)
items.next()
print(cse.pages.current.items.title)
items.next()
print(cse.pages.current.items.title)
items.next()
print(cse.pages.current.items.title)
items.next()
print(cse.pages.current.items.title)
items.next()
print(cse.pages.current.items.title)
items.next()
items.previous()
print(cse.pages.current.items.title)
items.previous()
print(cse.pages.current.items.title)
items.previous()
print(cse.pages.current.items.title)
items.previous()
print(cse.pages.current.items.title)
items.previous()
print(cse.pages.current.items.title)
items.previous()
print(cse.pages.current.items.title)
items.previous()
print(cse.pages.current.items.title)
items.previous()
print(cse.pages.current.items.title)
items.previous()
print(cse.pages.current.items.title)

print(items.title)
print(cse.pages.current.title)

print(items.next().title)

print(cse.pages.current.title)
print(cse.start)

cse._test_feed = page2
cse.next()
print(cse.pages.current.title)
print(cse.start)
print('sdf')
print(cse.pages)
print(str(cse.pages._current_index))
print(cse.pages.current.items)
print(len(cse.pages))
print(items._current_index)
cse.previous()
print(cse.pages)
cse.next()
page = cse.next()
print(page.items.next().title)
while True:
    try:
        print(page.items.next().title)
    except:
        break
