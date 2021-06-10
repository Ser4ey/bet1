bet_type = 'Команда 2 Тб(534)'
reverse_bet = 'Unknown bet'

if bet_type == 'П1' or bet_type == '1':
    #  1 -> X2
    reverse_bet = 'X2'

elif bet_type == '2' or bet_type == 'П2':
    #  2 -> 1X
    reverse_bet = '1X'

elif bet_type == 'X' or bet_type == 'Х':
    #  X -> 12
    reverse_bet = '12'

elif bet_type == '1X' or bet_type == '1Х':
    #  1X -> 2
    reverse_bet = '2'

elif bet_type == 'Х2' or bet_type == 'X2':
    #  X2 -> 1
    reverse_bet = '1'

elif bet_type == '12' or bet_type == '21':
    #  12 -> X
    reverse_bet = 'X'

elif bet_type[:13] == 'Гола не будет':
    #  Гола не будет(3) -> Тм(2.5)
    reverse_bet = bet_type.split('(')[-1]
    reverse_bet = reverse_bet.strip(')')
    reverse_bet = int(reverse_bet) + 0.5
    reverse_bet = str(reverse_bet)
    reverse_bet = f'Тм({reverse_bet})'

elif bet_type == 'Чет':
    #  Чет -> Нечет
    reverse_bet = 'Нечет'

elif bet_type == 'Нечет':
    #  Чет -> Нечет
    reverse_bet = 'Чет'

else:
    if 'Команда' in bet_type:
        if 'Тб' in bet_type:
            reverse_bet = bet_type.replace('Тб', 'Тм')
        elif 'Тм' in bet_type:
            reverse_bet = bet_type.replace('Тм', 'Тб')

    elif 'Тб' in bet_type:
        reverse_bet = bet_type.replace('Тб', 'Тм')

    elif 'Тм' in bet_type:
        reverse_bet = bet_type.replace('Тм', 'Тб')


print(reverse_bet)