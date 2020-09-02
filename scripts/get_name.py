try:
    x = input()
    while x == '':
        x = input()
    while x != '':
        print (x.split('/')[0])
        x = input()
except EOFError:
    pass
#print (raw_input().split('/')[0])

