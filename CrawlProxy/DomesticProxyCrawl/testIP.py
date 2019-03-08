def test():
    for i in range(10):
        try:
            print(i)
            if i == 11:
                return 'dasda'
        except:
            pass
    else:
        return 'sadasdsad'


print(test())