from settings import logging


async def check_for_empty_list(result):
    return result == []


async def packer(unpacked_list):

    pack_list = []
    packing = []

    list_size = len(unpacked_list)
    stop_los = list_size % 5
    for i in range(list_size):
        
        if i == stop_los and stop_los != 0:
            pack_list.append(packing)
            packing = []

        elif (i - stop_los) % 5 == 0 and i != 0:
            pack_list.append(packing)
            packing = []

        packing.append(unpacked_list[i])

        if list_size - i == 1:
            pack_list.append(packing)
            packing = []

    return pack_list
