from decimal import Decimal


# remove zero
def digital_utils(temps):
    temps = str(temps)
    if temps.find('E'):
        temps = '{:.8f}'.format(Decimal(temps))
    nums = temps.split('.')
    if int(nums[1]) == 0:
        return nums[0]
    else:
        num = str(int(nums[1][::-1]))
        result = '{}.{}'.format(nums[0], num[::-1])
        return result
