import pytest
from .main import DataAnalysis

test_list = [
             ["Pomorskie","przystąpiło","kobiety","2012","10"],
             ["Pomorskie","zdało","kobiety","2012","9"],
             ["Pomorskie","przystąpiło","mężczyźni","2012","5"],
             ["Pomorskie","zdało","mężczyźni","2012","5"],

             ["Pomorskie", "przystąpiło", "kobiety", "2013", "11"],
             ["Pomorskie", "zdało", "kobiety", "2013", "10"],
             ["Pomorskie", "przystąpiło", "mężczyźni", "2013", "6"],
             ["Pomorskie", "zdało", "mężczyźni", "2013", "5"],

             ["Śląskie","przystąpiło","kobiety","2012","20"],
             ["Śląskie","zdało","kobiety","2012","9"],
             ["Śląskie","przystąpiło","mężczyźni","2012","25"],
             ["Śląskie","zdało","mężczyźni","2012","5"],

             ["Śląskie", "przystąpiło", "kobiety", "2013", "8"],
             ["Śląskie", "zdało", "kobiety", "2013", "8"],
             ["Śląskie", "przystąpiło", "mężczyźni", "2013", "9"],
             ["Śląskie", "zdało", "mężczyźni", "2013", "5"]
             ]


def test_average_num():
    a = DataAnalysis()
    for item in test_list:
        a.record_list.append(DataAnalysis.Record(item))

    assert a.average_number("Pomorskie",2012) == 15
    assert a.average_number("Pomorskie",2013) == (10+5+11+6)/2
    assert a.average_number("Śląskie",2012, a.men) == 25
    assert a.average_number("Śląskie",2013, a.women) == 14


def test_average_percent():
    a = DataAnalysis()
    for item in test_list:
        a.record_list.append(DataAnalysis.Record(item))

    assert a.average_percent("Pomorskie") == [{"years": 2012, "ratio": (14/15*100)}, {"years": 2013, "ratio": (15/17*100)}]
    assert a.average_percent("Śląskie", "kobiety") == [{"years": 2012, "ratio": (9/20*100)}, {"years":2013, "ratio": (8/8*100)}]


def test_best_pass_rate():
    a = DataAnalysis()
    for item in test_list:
        a.record_list.append(DataAnalysis.Record(item))

    assert a.best_pass_rate(2012) == "Pomorskie"
    assert a.best_pass_rate(2012, "kobiety") == "Pomorskie"
    assert a.best_pass_rate(2013, "kobiety") == "Śląskie"
    assert a.best_pass_rate(2013, "mężczyźni") == "Pomorskie"


def test_get_regression():
    a = DataAnalysis()
    for item in test_list:
        a.record_list.append(DataAnalysis.Record(item))

    assert a.get_regression() == [{'territory': 'Pomorskie', 'years_1': 2012, 'years_2': 2013}]
    assert a.get_regression("kobiety") == []


def test_compare():
    a = DataAnalysis()
    for item in test_list:
        a.record_list.append(DataAnalysis.Record(item))

    assert a.compare_hybrid("Pomorskie", "Śląskie") == [{'territory': 'Pomorskie', 'years': 2012}, {'territory': 'Pomorskie', 'years': 2013}]
    assert a.compare_hybrid("Śląskie", "Pomorskie", "kobiety") == [{'territory': 'Pomorskie', 'years': 2012}, {'territory': 'Śląskie', 'years': 2013}]


