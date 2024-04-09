import warnings
from .constants import MAD_CONFORM


def _inform_(df, high_Z, conf):
    """Выбирает и сортирует по выбранным Z_stats, информируя или нет.
    """

    if isinstance(high_Z, int):
        if conf is not None:
            dd = df[['Expected', 'Found', 'Z_score'
                     ]].sort_values('Z_score', ascending=False).head(high_Z)
            print(f'\nЭлементы с наибольшими {high_Z} Z-значениями:\n')
        # Тест суммирования
        else:
            dd = df[['Expected', 'Found', 'AbsDif'
                     ]].sort_values('AbsDif', ascending=False
                                    ).head(high_Z)
            print(f'\nЭлементы с наибольшими {high_Z} абсолютными отклонениями:\n')
    else:
        if high_Z == 'pos':
            m1 = df.Dif > 0
            m2 = df.Z_score > conf
            dd = df[['Expected', 'Found', 'Z_score'
                     ]].loc[m1 & m2].sort_values('Z_score', ascending=False)
            print('\nЭлементы с значимыми положительными отклонениями:\n')
        elif high_Z == 'neg':
            m1 = df.Dif < 0
            m2 = df.Z_score > conf
            dd = df[['Expected', 'Found', 'Z_score'
                     ]].loc[m1 & m2].sort_values('Z_score', ascending=False)
            print('\nЭлементы с значимыми отрицательными отклонениями:\n')
        else:
            dd = df[['Expected', 'Found', 'Z_score'
                     ]].loc[df.Z_score > conf].sort_values('Z_score',
                                                           ascending=False)
            print('\nЭлементы с значимыми отклонениями:\n')
    print(dd)


def _report_mad_(digs, MAD):
    """Отчет о среднем абсолютном отклонении теста и сравнение его с критическими значениями
    """
    print(f'Среднее абсолютное отклонение: {MAD:.6f}')
    if digs != -2:
        mads = MAD_CONFORM[digs]
        if MAD <= mads[0]:
            print(f'MAD <= {mads[0]:.6f}: Тесное соответствие.\n')
        elif MAD <= mads[1]:
            print(f'{mads[0]:.6f} < MAD <= {mads[1]:.6f}: '
                  'Приемлемое соответствие.\n')
        elif MAD <= mads[2]:
            print(f'{mads[1]:.6f} < MAD <= {mads[2]:.6f}: '
                  'С погрешностью приемлемое соответствие.\n')
        else:
            print(f'MAD > {mads[2]:.6f}: Несоответствие.\n')
    else:
        print("Для этого теста нет проверки соответствия среднему абсолютному отклонению.\n")


def _report_KS_(KS, crit_KS):
    """Отчет о статистике теста Колмогорова-Смирнова и сравнение ее с критическими
    значениями, в зависимости от уровня доверия
    """
    result = 'PASS' if KS <= crit_KS else 'FAIL'
    print(f"\n\tКолмогоров-Смирнов: {KS:.6f}",
          f"\n\tКритическое значение: {crit_KS:.6f} -- {result}")


def _report_chi2_(chi2, CRIT_CHI2):
    """Отчет о статистике теста хи-квадрат и сравнение ее с критическими значениями,
    в зависимости от уровня доверия
    """
    result = 'PASS' if chi2 <= CRIT_CHI2 else 'FAIL'
    print(f"\n\tХи-квадрат: {chi2:.6f}",
          f"\n\tКритическое значение: {CRIT_CHI2:.6f} -- {result}")


def _report_Z_(df, high_Z, crit_Z):
    """Отчет о Z-значениях теста и сравнение их с критическим значением,
    в зависимости от уровня доверия
    """
    print(f"\n\tКритическое Z-значение:{crit_Z}.")
    _inform_(df, high_Z, crit_Z)


def _report_summ_(test, high_diff):
    """Отчет о тесте суммирования абсолютных разностей между найденными и
    ожидаемыми долями

    """
    if high_diff is not None:
        print(f'\nНаибольшие {high_diff} абсолютные разности:\n')
        print(test.sort_values('AbsDif', ascending=False).head(high_diff))
    else:
        print('\nНаибольшие абсолютные разности:\n')
        print(test.sort_values('AbsDif', ascending=False))


def _report_bhattac_coeff_(bhattac_coeff):
    """
    """
    print(f"Коэффициент Бхаттачарьи: {bhattac_coeff:6f}\n")


def _report_bhattac_dist_(bhattac_dist):
    """
    """
    print(f"Расстояние Бхаттачарьи: {bhattac_dist:6f}\n")


def _report_kl_diverg_(kl_diverg):
    """
    """
    print(f"Дивергенция Куллбака-Лейблера: {kl_diverg:6f}\n")


def _report_test_(test, high=None, crit_vals=None):
    """Основная отчетная функция. Получает аргументы для отчета, инициирует
    процесс и вызывает нужную отчетную вспомогательную функцию(ии), в зависимости
    от Теста.
    """
    print('\n', f'  {test.name}  '.center(50, '#'), '\n')
    if not 'Summation' in test.name:
        _report_mad_(test.digs, test.MAD)
        _report_bhattac_coeff_(test.bhattacharyya_coefficient)
        _report_bhattac_dist_(test.bhattacharyya_distance)
        _report_kl_diverg_(test.kullback_leibler_divergence)
        if test.confidence is not None:
            print(f"Для уровня доверия {test.confidence}%: ")
            _report_KS_(test.KS, crit_vals['KS'])
            _report_chi2_(test.chi_square, crit_vals['chi2'])
            _report_Z_(test, high, crit_vals['Z'])
        else:
            print('Уровень доверия в настоящее время `None`. Задайте уровень доверия, '
                  'чтобы сгенерировать сравнимые критические значения.')
            if isinstance(high, int):
                _inform_(test, high, None)
    else:
        _report_summ_(test, high)


def _report_mantissa_(stats, confidence):
    """Выводит статистику мантисс и их соответствующие справочные значения

    Args:
        stats (dict):
    """
    print("\n", '  Тест мантисс  '.center(52, '#'))
    print(f"\nСреднее значение мантисс равно      {stats['Mean']:.6f}."
          "\tСправ.: 0.5")
    print(f"Дисперсия мантисс равна  {stats['Var']:.6f}."
          "\tСправ.: 0.08333")
    print(f"Коэффициент асимметрии мантисс равен  {stats['Skew']:.6f}."
          "\tСправ.: 0.0")
    print(f"Коэффициент эксцесса мантисс равен  {stats['Kurt']:.6f}."
          "\tСправ.: -1.2")
    print("\nСтатистика Колмогорова-Смирнова для распределения мантисс"
          f" равна {stats['KS']:.6f}.\nКритическое значение для уровня доверия "
          f"{confidence}% равно {stats['KS_critical']:.6f} -- "
          f"{'PASS' if stats['KS'] < stats['KS_critical'] else 'FAIL'}\n")


def _deprecate_inform_(verbose, inform):
    """
    Рaises:
        FutureWarning: если используется аргумент `inform` (будет удален в будущих версиях).
    """
    if inform is None:
        return verbose
    else:
        warnings.warn('Параметр `inform` будет удален в будущих версиях. Используйте `verbose` вместо него.',
                      FutureWarning)
        return inform
