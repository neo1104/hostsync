def str_to_list(s):
    l = []
    tmp = s.strip('[]').split(',')
    for i in tmp:
        l.append(i.strip().strip("'"))
    return l
