recirc = 0
while recirc <= 1:

    onsorter = 0
    cartons = 0
    induct_rate = 700
    sorter_capacity = 1700
    for i in range(0,100):
        
        if onsorter < sorter_capacity:
            cartons += induct_rate*(1-recirc)
            onsorter += induct_rate*(recirc)
        else:
            onsorter -= induct_rate*(1-recirc)
    print(f"Recirc: {recirc}, On Sorter: {onsorter}, Cartons: {cartons}")


    recirc += .1