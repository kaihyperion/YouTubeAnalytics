import os
import json



def main(**kwargs):
    for kw in kwargs:
        print(kw, '-', kwargs[kw])


if __name__ == "__main__":
    main(a = 24, b = 87, c =3, d =46)
    

#kwargs is a pararmeter name and acts liek a dictioanry
# kwargs is like keyword (named) arguemnts. so key and value. must have '=' equla sign
# ** is the 'unpacking operator' it unpacks the argument passed as dictionary
# *args is positional argument