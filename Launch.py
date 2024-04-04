import os
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
from tkinter import ttk
import pandas as pd
from datetime import datetime
import warnings
from plot import create_plot
warnings.filterwarnings("ignore", category=FutureWarning)

result_df = pd.DataFrame(
            columns=['保障节点名称', '总样本数', '满足局方标准的比例', '时间晚于基准字段的样本数量',
                     '时间晚于基准字段的样本占比', '时间早于基准字段的样本数量',
                     '时间早于基准字段的样本占比',
                     '平均值', '95%位次值', '90%位次值', '85%位次值', '80%位次值', '75%位次值', '70%位次值',
                     '65%位次值', '60%位次值',
                     '55%位次值', '50%位次值', '45%位次值', '40%位次值', '35%位次值', '30%位次值', '25%位次值',
                     '20%位次值', '15%位次值',
                     '10%位次值', '5%位次值', '95%位次值对应航班占比', '90%位次值对应航班占比', '85%位次值对应航班占比',
                     '80%位次值对应航班占比',
                     '75%位次值对应航班占比', '70%位次值对应航班占比', '65%位次值对应航班占比', '60%位次值对应航班占比',
                     '55%位次值对应航班占比',
                     '50%位次值对应航班占比', '45%位次值对应航班占比', '40%位次值对应航班占比', '35%位次值对应航班占比',
                     '30%位次值对应航班占比',
                     '25%位次值对应航班占比', '20%位次值对应航班占比', '15%位次值对应航班占比', '10%位次值对应航班占比',
                     '5%位次值对应航班占比'])

# 定义计算满足比例函数
def total(Y, min, max, name, T, ccsv):
    total = len(Y) + T
    count = sum(min <= value <= max for value in Y) + T
    try:
        percentage = count / total
        data = [name, total, percentage]
        # 将结果添加到数据框
        global result_df
        result_df.loc[ccsv, result_df.columns[:3]] = data
    except:
        return
    #result_df = result_df.append(pd.Series(data, index=result_df.columns[:3]), ignore_index=True)

# 定义计算百分位值和比例函数
def perc(Y, mode, ccsv):
    if len(Y) == 0:
        messagebox.showinfo("错误", "无符合条件的计算位次值样本！")
        return
    mean = pd.Series(Y).mean()
    xs = [pd.Series(Y).quantile(0.05 * factor) for factor in range(1, 20)]
    xs = [round(x) for x in xs]
    # 衔接或持续类
    if mode == -1:
        ys = list(map(lambda x: sum(value <= x for value in Y) / len(Y), xs))
    # 驱动类
    elif mode == 1:
        ys = list(map(lambda x: sum(value >= x for value in Y) / len(Y), xs))
    data = [mean] + xs[::-1] + ys[::-1]
    global result_df
    result_df.loc[ccsv, result_df.columns[7:46]] = data
    #result_df = result_df.append(pd.Series(data, index=result_df.columns[7:46]), ignore_index=True)

# 定义基准字段早晚
def jf(Y, mode, ccsv):
    global result_df
    if mode == 1:
        total = len(Y)
        if total == 0:
            messagebox.showinfo("错误", "无符合条件的样本！")
            return
        countl = sum(0 > value for value in Y)
        counte = sum(value > 0 for value in Y)
        data = [countl, countl/total, counte, counte/total]
        result_df.loc[ccsv, result_df.columns[3:7]] = data
        #result_df = result_df.append(pd.Series(data, index=result_df.columns[3:7]), ignore_index=True)
    else:
        data = ['', '', '', '']
        result_df.loc[ccsv, result_df.columns[3:7]] = data
        #result_df = result_df.append(pd.Series(data, index=result_df.columns[3:7]), ignore_index=True)

#定义转换时间函数
def ct(time_str):
    time_object = datetime.strptime(time_str, "%H:%M")
    total_minutes = time_object.hour * 60 + time_object.minute
    return total_minutes

# 多输入参数处理
def multime(arr,mode):
    # 如果所有值都为空，什么都不做
    ttime = 0
    if all(value is None or value == "" for value in arr):
        return
    # 过滤掉空值，获取所有非空值
    non_empty_values = [value for value in arr if value is not None and value != ""]
    # 如果只有一个非空值，将其设为stime
    if len(non_empty_values) == 1:
        ttime = non_empty_values[0]
    else:
        if mode == 'min':
            ttime = min(non_empty_values)
        elif mode == 'max':
            ttime = max(non_empty_values)
    return ttime

# 计算模块
def cal(name,dataf,mode1,mode2,mode3,type,type1,start,end,startm=0):
    #name为环节名称
    #mode1=1为单输入指标，mode1=2为多输入指标
    #mode2=ABC为ABC机型，mode2=DEF为DEF机型，mode=0为不分机型
    #mode3=KS为仅开始节点，mode3=JS为仅结束节点，mode3=ALL为开始结束都是多输入,mode=0为非多输入指标
    #type=-1为持续类和衔接类，type=1为驱动类

    # 确定正常值和位次值范围
    valueread = pd.read_csv('正常值上下界读取.csv', header=0, encoding='gbk')
    standard = valueread.loc[valueread['涉及字段名称'] == name, '计算标准阈值'].values[0]
    zczup = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围上界'].values[0]
    zczlow = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围下界'].values[0]
    wczup = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围上界'].values[0]
    wczlow = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围下界'].values[0]
    if pd.isna(zczup):
        zczup = 120
    if pd.isna(zczlow):
        zczlow = 0
    if pd.isna(wczup):
        wczup = zczup
    if pd.isna(wczlow):
        wczlow = 0

    Y = []
    D = []
    T = 0
    #global countcsv

    if mode1 == 1:
        for i in range(0, len(dataf)):
            if mode2 == "ABC" and dataf.loc[i, '机型大类'] not in ['A', 'B', 'C']:
                continue
            elif mode2 == "DEF" and dataf.loc[i, '机型大类'] not in ['D', 'E', 'F']:
                continue
            elif mode2 == "AE" and dataf.loc[i, '机型大类'] not in ['A', 'B', 'C', 'D', 'E']:
                continue
            elif mode2 == "DE" and dataf.loc[i, '机型大类'] not in ['D', 'E']:
                continue
            elif mode2 == "F" and dataf.loc[i, '机型大类'] not in ['F']:
                continue
            if not pd.isna(dataf.loc[i, start]) and not pd.isna(dataf.loc[i, end]):
                if dataf.loc[i, start] == 'T' or dataf.loc[i, end] == 'T':
                    T += 1
                else:
                    try:
                        a = (ct(dataf.loc[i, end]) - ct(dataf.loc[i, start]))
                    except:
                        continue
                    if a < -1380:
                        a += 1440
                    if type1 == 1 and a == 0:
                        a += 1
                    if zczlow <= a <= zczup:
                        Y.append(a)
                    if wczlow < a <= wczup:
                        D.append(a)
        if type == 1:
            total(Y, standard, zczup, name, T, 0)
        elif type == -1:
            total(Y, 0, standard, name, T, 0)
        jf(Y, type, 0)
        perc(D, type, 0)
        #0 += 1
    elif mode1 == 2:
        stime = 0
        etime = 0
        for i in range(0, len(dataf)):
            if mode2 == "ABC" and dataf.loc[i, '机型大类'] not in ['A', 'B', 'C']:
                continue
            elif mode2 == "DEF" and dataf.loc[i, '机型大类'] not in ['D', 'E', 'F']:
                continue
            elif mode2 == "DE" and dataf.loc[i, '机型大类'] not in ['D', 'E']:
                continue
            elif mode2 == "F" and dataf.loc[i, '机型大类'] not in ['F']:
                continue
            if type == 1:
                for sname in start:
                    if dataf.loc[i, sname] == 'T':
                        T += 1
                        continue
            ary = []
            if mode3 == 'KS':
                if startm == 0:
                    for sname in start:
                        if dataf.loc[i, sname] != '':
                            ary.append(dataf.loc[i, sname])
                    if ary:
                        stime = min(ary)
                        etime = dataf.loc[i, end]
                    else:
                        continue
                if startm == 1:
                    for sname in start:
                        if dataf.loc[i, sname] != '':
                            ary.append(dataf.loc[i, sname])
                    if ary:
                        stime = max(ary)
                        etime = dataf.loc[i, end]
                    else:
                        continue
            elif mode3 == 'JS':
                for ename in end:
                    if dataf.loc[i, ename] != '':
                        ary.append(dataf.loc[i, ename])
                if ary:
                    stime = dataf.loc[i, start]
                    etime = max(ary)
                else:
                    continue
            elif mode3 == 'ALL':
                sary = []
                eary = []
                for sname in start:
                    if dataf.loc[i, sname] != '':
                        sary.append(dataf.loc[i, sname])
                for ename in end:
                    if dataf.loc[i, ename] != '':
                        eary.append(dataf.loc[i, ename])
                if sary and eary:
                    stime = min(sary)
                    etime = max(eary)
                else:
                    continue
            try:
                a = (ct(etime) - ct(stime))
            except:
                continue
            if a < -1380:
                a += 1440
            if type1 == 1 and a == 0:
                a += 1
            if zczlow <= a <= zczup:
                Y.append(a)
            if wczlow < a <= wczup:
                D.append(a)
        if type == 1:
            total(Y, standard, zczup, name, T, 0)
        elif type == -1:
            total(Y, 0, standard, name, T, 0)
        jf(Y, type, 0)
        perc(D, type, 0)
        #0 += 1

# 特殊计算模块——廊桥、客梯车
def cal_shu(name,dataf,sl,slname,start,end):
    # 确定正常值和位次值范围
    valueread = pd.read_csv('正常值上下界读取.csv', header=0, encoding='gbk')
    standard = valueread.loc[valueread['涉及字段名称'] == name, '计算标准阈值'].values[0]
    zczup = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围上界'].values[0]
    zczlow = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围下界'].values[0]
    wczup = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围上界'].values[0]
    wczlow = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围下界'].values[0]
    if pd.isna(zczup):
        zczup = 120
    if pd.isna(zczlow):
        zczlow = 0
    if pd.isna(wczup):
        wczup = zczup
    if pd.isna(wczlow):
        wczlow = 0

    Y = []
    D = []
    T = 0
    stime = 0
    etime = 0
    #global countcsv

    for i in range(0, len(dataf)):
        if slname == "廊桥数量" or slname == "客梯车数量":
            if sl == 1 and str(dataf.loc[i, slname]) != '1' and str(dataf.loc[i, slname]) != '1.0':
                continue
            if sl == 2 and str(dataf.loc[i, slname]) != '2' and str(dataf.loc[i, slname]) != '2.0':
                continue
            if sl == 3 and str(dataf.loc[i, slname]) != '3' and str(dataf.loc[i, slname]) != '3.0':
                continue
        # elif slname == "客梯车数量":
        #     if sl == 1 and dataf.loc[i, slname] != 1:
        #         continue
        #     if sl == 2 and dataf.loc[i, slname] != 2:
        #         continue
        #     if sl == 3 and dataf.loc[i, slname] != 3:
        #         continue

    # for i in range(0, len(dataf)):
    #     if sl == 1 and not pd.notna(dataf.loc[i, slname]):
    #         if dataf.loc[i, slname] != '1':
    #             print(i)
    #             continue
    #     if sl == 2 and not pd.notna(dataf.loc[i, slname]):
    #         if dataf.loc[i, slname] != '2':
    #             continue
    #     if sl == 3 and not pd.notna(dataf.loc[i, slname]):
    #         if dataf.loc[i, slname] != '3':
    #             continue
        sary = []
        eary = []
        for sname in start:
            if dataf.loc[i, sname] != '':
                sary.append(dataf.loc[i, sname])
        for ename in end:
            if dataf.loc[i, ename] != '':
                eary.append(dataf.loc[i, ename])

        try:
            stime = min(sary)
            etime = max(eary)
            a = (ct(etime) - ct(stime))
        except:
            continue
        if a < -1380:
            a += 1440
        if a == 0:
            a += 1
        if zczlow <= a <= zczup:
            Y.append(a)
        if wczlow < a <= wczup:
            D.append(a)
    if len(D) == 0:
        messagebox.showerror("错误", "无满足条件数据，无法计算！")
        return
    total(Y, 0, standard, name, T, 0)
    jf(Y, -1, 0)
    perc(D, -1, 0)

# 特殊计算模块——是否载客加油及加油完成时间
def cal_jiayou(name,dataf,zaike,start,end):
    # 确定正常值和位次值范围
    valueread = pd.read_csv('正常值上下界读取.csv', header=0, encoding='gbk')
    standard = valueread.loc[valueread['涉及字段名称'] == name, '计算标准阈值'].values[0]
    zczup = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围上界'].values[0]
    zczlow = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围下界'].values[0]
    wczup = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围上界'].values[0]
    wczlow = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围下界'].values[0]
    if pd.isna(zczup):
        zczup = 120
    if pd.isna(zczlow):
        zczlow = 0
    if pd.isna(wczup):
        wczup = zczup
    if pd.isna(wczlow):
        wczlow = 0

    Y = []
    D = []
    T = 0
    #global countcsv

    for i in range(0, len(dataf)):
        if not pd.isna(dataf.loc[i, '是否载客加油']):
            if zaike == 1 and dataf.loc[i, '是否载客加油'] != 1 and dataf.loc[i, '是否载客加油'] != '1':
                continue
            elif zaike == 0 and dataf.loc[i, '是否载客加油'] != 0 and dataf.loc[i, '是否载客加油'] != '0':
                continue
        else:
            continue
        try:
            a = (ct(dataf.loc[i, end]) - ct(dataf.loc[i, start]))
        except:
            continue
        if a < -1380:
            a += 1440
        if zczlow <= a <= zczup:
            Y.append(a)
        if wczlow < a <= wczup:
            D.append(a)
    total(Y, standard, zczup, name, T, 0)
    jf(Y, 1, 0)
    perc(D, 1, 0)

# 特殊计算模块——登机口开放
def cal_djk(name,dataf,jw,mode,start,end):
    #mode=F时仅计算F机型，mode=AE时计算A-E机型，mode=0时计算所有机型
    # 确定正常值和位次值范围
    valueread = pd.read_csv('正常值上下界读取.csv', header=0, encoding='gbk')
    standard = valueread.loc[valueread['涉及字段名称'] == name, '计算标准阈值'].values[0]
    zczup = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围上界'].values[0]
    zczlow = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围下界'].values[0]
    wczup = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围上界'].values[0]
    wczlow = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围下界'].values[0]
    if pd.isna(zczup):
        zczup = 120
    if pd.isna(zczlow):
        zczlow = 0
    if pd.isna(wczup):
        wczup = zczup
    if pd.isna(wczlow):
        wczlow = 0

    Y = []
    D = []
    T = 0
    #global countcsv

    for i in range(0, len(dataf)):
        if not pd.isna(dataf.loc[i, '出港近远机位']) and not pd.isna(dataf.loc[i, '机型大类']):
            if jw == '近' and dataf.loc[i, '出港近远机位'] != '近':
                continue
            elif jw == '远' and dataf.loc[i, '出港近远机位'] != '远':
                continue
            if mode == 'AE' and dataf.loc[i, '机型大类'] not in ['A', 'B', 'C', 'D', 'E']:
                continue
            elif mode == 'F' and dataf.loc[i, '机型大类'] != 'F':
                continue
        else:
            continue
        try:
            a = (ct(dataf.loc[i, end]) - ct(dataf.loc[i, start]))
        except:
            continue
        if a < -1380:
            a += 1440
        if zczlow <= a <= zczup:
            Y.append(a)
        if wczlow < a <= wczup:
            D.append(a)
    total(Y, standard, zczup, name, T, 0)
    jf(Y, 1, 0)
    perc(D, 1, 0)

# 特殊计算模块——推离机位
def cal_tc(name,dataf,mode,start,end):
    #mode=1时已对接，mode=0时未对接
    # 确定正常值和位次值范围
    valueread = pd.read_csv('正常值上下界读取.csv', header=0, encoding='gbk')
    standard = valueread.loc[valueread['涉及字段名称'] == name, '计算标准阈值'].values[0]
    zczup = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围上界'].values[0]
    zczlow = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围下界'].values[0]
    wczup = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围上界'].values[0]
    wczlow = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围下界'].values[0]
    if pd.isna(zczup):
        zczup = 120
    if pd.isna(zczlow):
        zczlow = 0
    if pd.isna(wczup):
        wczup = zczup
    if pd.isna(wczlow):
        wczlow = 0

    Y = []
    D = []
    T = 0
    #global countcsv

    for i in range(0, len(dataf)):
        try:
            if dataf.loc[i, '牵引车对接结束'] != '' and dataf.loc[i, '防撞灯闪烁'] != '':
                if mode == 1 and (ct(dataf.loc[i, '牵引车对接结束']) - ct(dataf.loc[i, '防撞灯闪烁'])) < 0:
                    continue
                elif mode == 0 and (ct(dataf.loc[i, '牵引车对接结束']) - ct(dataf.loc[i, '防撞灯闪烁'])) >= 0:
                    continue
            else:
                continue
        except:
            continue
        try:
            a = (ct(dataf.loc[i, end]) - ct(dataf.loc[i, start]))
        except:
            continue
        if a < -1380:
            a += 1440
        if zczlow <= a <= zczup:
            Y.append(a)
        if wczlow < a <= wczup:
            D.append(a)
    total(Y, standard, zczup, name, T, 0)
    jf(Y, 1, 0)
    perc(D, 1, 0)

# 特殊计算模块——不满足快速过站是否满足条件
def cal_ksgz(name,dataf,mode1,mode2,mode3,type,type1,start,end,startm=0,jw='不区分'):
    # mode=DEF时仅计算DEF机型，mode=ABC时计算ABC机型，mode=0时计算所有机型
    # 确定正常值和位次值范围
    valueread = pd.read_csv('正常值上下界读取.csv', header=0, encoding='gbk')
    standard = valueread.loc[valueread['涉及字段名称'] == name, '计算标准阈值'].values[0]
    zczup = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围上界'].values[0]
    zczlow = valueread.loc[valueread['涉及字段名称'] == name, '正常值范围下界'].values[0]
    wczup = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围上界'].values[0]
    wczlow = valueread.loc[valueread['涉及字段名称'] == name, '统计位次值范围下界'].values[0]
    if pd.isna(zczup):
        zczup = 120
    if pd.isna(zczlow):
        zczlow = 0
    if pd.isna(wczup):
        wczup = zczup
    if pd.isna(wczlow):
        wczlow = 0

    Y = []
    D = []
    T = 0

    if mode1 == 1:
        for i in range(0, len(dataf)):
            if mode2 == 'ABC':
                try:
                    if dataf.loc[i, '机型大类'] not in ['A', 'B', 'C']:
                        continue
                    # ABC机型快速过站时间小于65min
                    if not ct(dataf.loc[i, 'STD']) - ct(dataf.loc[i, 'STA']) < 65:
                        continue
                except:
                    continue
            elif mode2 == 'DEF':
                try:
                    if dataf.loc[i, '机型大类'] not in ['D', 'E', 'F']:
                        continue
                    # ABC机型快速过站时间小于75min
                    if not ct(dataf.loc[i, 'STD']) - ct(dataf.loc[i, 'STA']) < 75:
                        continue
                except:
                    continue
            if jw == '近' and dataf.loc[i, '出港近远机位'] != '近':
                continue
            elif jw == '远' and dataf.loc[i, '出港近远机位'] != '远':
                continue
            if not pd.isna(dataf.loc[i, start]) and not pd.isna(dataf.loc[i, end]):
                if dataf.loc[i, start] == 'T' or dataf.loc[i, end] == 'T':
                    T += 1
                else:
                    try:
                        a = (ct(dataf.loc[i, end]) - ct(dataf.loc[i, start]))
                    except:
                        continue
                    if a < -1380:
                        a += 1440
                    if type1 == 1 and a == 0:
                        a += 1
                    if zczlow <= a <= zczup:
                        Y.append(a)
                    if wczlow < a <= wczup:
                        D.append(a)
        if type == 1:
            total(Y, standard, zczup, name, T, 0)
        elif type == -1:
            total(Y, 0, standard, name, T, 0)
        jf(Y, type, 0)
        perc(D, type, 0)
        #0 += 1
    elif mode1 == 2:
        stime = 0
        etime = 0
        for i in range(0, len(dataf)):
            if mode2 == 'ABC':
                try:
                    if dataf.loc[i, '机型大类'] not in ['A', 'B', 'C']:
                        continue
                    if not ct(dataf.loc[i, 'STD']) - ct(dataf.loc[i, 'STA']) < 65:
                        continue
                except:
                    continue
            elif mode2 == 'DEF':
                try:
                    if dataf.loc[i, '机型大类'] not in ['D', 'E', 'F']:
                        continue
                    if not ct(dataf.loc[i, 'STD']) - ct(dataf.loc[i, 'STA']) < 75:
                        continue
                except:
                    continue
            if jw == '近' and dataf.loc[i, '出港近远机位'] != '近':
                continue
            elif jw == '远' and dataf.loc[i, '出港近远机位'] != '远':
                continue
            if mode2 == "ABC" and dataf.loc[i, '机型大类'] not in ['A', 'B', 'C']:
                continue
            elif mode2 == "DEF" and dataf.loc[i, '机型大类'] not in ['D', 'E', 'F']:
                continue
            if type == 1:
                for sname in start:
                    if dataf.loc[i, sname] == 'T':
                        T += 1
                        continue
            ary = []
            if mode3 == 'KS':
                if startm == 0:
                    for sname in start:
                        if dataf.loc[i, sname] != '':
                            ary.append(dataf.loc[i, sname])
                    if ary:
                        stime = min(ary)
                        etime = dataf.loc[i, end]
                    else:
                        continue
                if startm == 1:
                    for sname in start:
                        if dataf.loc[i, sname] != '':
                            ary.append(dataf.loc[i, sname])
                    if ary:
                        stime = max(ary)
                        etime = dataf.loc[i, end]
                    else:
                        continue
            elif mode3 == 'JS':
                for ename in end:
                    if dataf.loc[i, ename] != '':
                        ary.append(dataf.loc[i, ename])
                if ary:
                    stime = dataf.loc[i, start]
                    etime = max(ary)
                else:
                    continue
            elif mode3 == 'ALL':
                sary = []
                eary = []
                for sname in start:
                    if dataf.loc[i, sname] != '':
                        sary.append(dataf.loc[i, sname])
                for ename in end:
                    if dataf.loc[i, ename] != '':
                        eary.append(dataf.loc[i, ename])
                if sary and eary:
                    stime = min(sary)
                    etime = max(eary)
                else:
                    continue
            try:
                a = (ct(etime) - ct(stime))
            except:
                continue
            if a < -1380:
                a += 1440
            if type1 == 1 and a == 0:
                a += 1
            if zczlow <= a <= zczup:
                Y.append(a)
            if wczlow < a <= wczup:
                D.append(a)
        if type == 1:
            total(Y, standard, zczup, name, T, 0)
        elif type == -1:
            total(Y, 0, standard, name, T, 0)
        jf(Y, type, 0)
        perc(D, type, 0)

####################################################################################################
# 定义处理UI的函数
def process_file():
    #try:
    #csv写入计数器
    # 获取用户输入的导入路径
    input_file_path = input_path_entry.get()
    # 检查是否选择了导入路径
    if not input_file_path:
        messagebox.showinfo("提示", "未选择导入路径，请重试。")
        return
    # 获取用户输入的导出路径
    output_file_path = output_path_entry.get()
    # 检查是否选择了导出路径
    # if not output_file_path:
    #     messagebox.showinfo("提示", "未选择导出路径，请重试。")
    #     return
    #读取csv文件
    try:
        dataf = pd.read_csv(input_file_path, header=0, encoding='gbk',na_filter=False)
        dataf['客梯车数量'] = dataf['客梯车数量'].astype(str)
    except:
        messagebox.showinfo("错误", "导入文件异常，请检查文件后再试。")
        return

    if airlines_entry.get() != ' ':
        dataf['进港航班号'] = dataf['进港航班号'].fillna('NA')
        dataf['离港航班号'] = dataf['离港航班号'].fillna('NA')
        dataf = dataf[(dataf['进港航班号'].str[:2] == airlines_entry.get()) | (dataf['离港航班号'].str[:2] == airlines_entry.get())]
    if agent_entry.get() != ' ':
        dataf = dataf[dataf['保障代理'] == agent_entry.get()]
    if stand_entry.get() != ' ':
        dataf = dataf[dataf['停机位'] == stand_entry.get()]
    if flight_entry.get() != ' ':
        dataf = dataf[dataf['航班性质'] == flight_entry.get()]

    if time_entry_1.get() != '':
        dataf['航班时间'] = pd.to_datetime(dataf['航班时间'])
        print(dataf['航班时间'])
        date_start = pd.to_datetime(time_entry_1.get())
        print(date_start)
        dataf = dataf[dataf['航班时间'] >= date_start]
    if time_entry_2.get() != '':
        try:
            dataf['航班时间'] = pd.to_datetime(dataf['航班时间'])
            date_end = pd.to_datetime(time_entry_2.get())
        except:
            date_end = pd.to_datetime(time_entry_2.get())
        dataf = dataf[dataf['航班时间'] <= date_end]
    dataf = dataf.reset_index(drop=True)

    # 获取勾选的选项
    selected_options = []
    selected_options.append(selected_option1.get())
    selected_options.append(selected_option_2.get())
    selected_options.append(selected_option_3.get())
    selected_options.append(selected_option_4.get())
    selected_options.append(selected_option_5.get())
    try:
        if "拖曳飞机到达出港机位" in selected_options:
            cal("过站机务到位", dataf, 1, 0, 0, 1, 0, '飞机入位机务到位', '上轮挡开始')
        elif "过站机务到位" in selected_options:
            cal("过站机务到位",dataf,1,0,0,1,0,'飞机入位机务到位','上轮挡开始')
        elif "轮挡、反光锥形标志物放置操作时间-ABC" in selected_options:
            cal("轮挡、反光锥形标志物放置操作时间-ABC",dataf,2,'ABC','ALL',-1,1,['上轮挡开始','摆反光锥开始'],['上轮挡结束','摆反光锥结束'])
        elif "轮挡、反光锥形标志物放置操作时间-DEF" in selected_options:
            cal("轮挡、反光锥形标志物放置操作时间-DEF",dataf,2,'DEF','ALL',-1,1,['上轮挡开始','摆反光锥开始'],['上轮挡结束','摆反光锥结束'])
        elif "机务给指令与廊桥对接的衔接时间" in selected_options:
            cal("机务给指令与廊桥对接的衔接时间",dataf,2,0,'JS',-1,0,'给出对接手势',['桥1对接开始','桥2对接开始','桥3对接开始'])
        elif "单桥对接作业时间" in selected_options:
            cal_shu("单桥对接作业时间",dataf,1,'廊桥数量',['桥1对接开始','桥2对接开始','桥3对接开始'],['桥1对接结束','桥2对接结束','桥3对接结束'])
        # id5
        elif "双桥对接作业时间" in selected_options:
            cal_shu("双桥对接作业时间",dataf,2,'廊桥数量',['桥1对接开始','桥2对接开始','桥3对接开始'],['桥1对接结束','桥2对接结束','桥3对接结束'])
        elif "三桥对接作业时间" in selected_options:
           cal_shu("三桥对接作业时间",dataf,3,'廊桥数量',['桥1对接开始','桥2对接开始','桥3对接开始'],['桥1对接结束','桥2对接结束','桥3对接结束'])
        elif "客梯车到达机位时间" in selected_options:
            cal("客梯车到达机位时间",dataf,1,0,0,1,0,'客梯车到位','上轮挡开始')
        elif "机务给指令与客梯车对接的衔接时间" in selected_options:
            cal("机务给指令与客梯车对接的衔接时间",dataf,2,0,'JS',-1,0,'给出对接手势',['客梯车1对接开始','客梯车2对接开始','客梯车3对接开始'])
        elif "单客梯车对接操作时间" in selected_options:
            cal_shu("单客梯车对接操作时间",dataf,1,'客梯车数量',['客梯车1对接开始','客梯车2对接开始','客梯车3对接开始'],['客梯车1对接结束','客梯车2对接结束','客梯车3对接结束'])
        # id10
        elif "多客梯车对接操作时间" in selected_options:
            cal_shu("多客梯车对接操作时间",dataf,2,'客梯车数量',['客梯车1对接开始','客梯车2对接开始','客梯车3对接开始'],['客梯车1对接结束','客梯车2对接结束','客梯车3对接结束'])
        elif "首辆摆渡车到达机位时间" in selected_options:
            cal("首辆摆渡车到达机位时间",dataf,1,0,0,1,0,'首辆摆渡车到机位','上轮挡开始')
        elif "地服接机人员到位时间" in selected_options:
            cal("地服接机人员到位时间",dataf,1,0,0,1,0,'地服到位','上轮挡开始')
        elif "装卸人员及装卸设备到位时间" in selected_options:
            cal("装卸人员及装卸设备到位时间",dataf,1,0,0,1,0,'装卸人员到位','上轮挡开始')
        elif "开货门至卸行李货邮时间-ABC" in selected_options:
            cal("开货门至卸行李货邮时间-ABC",dataf, 2, 'ABC', 'JS', -1,0, '开货门',['卸行李开始', '卸货物开始'])
        # id15
        elif "开货门至卸行李货邮时间-DEF" in selected_options:
            cal("开货门至卸行李货邮时间-DEF",dataf, 2, 'DEF', 'JS', -1,0, '开货门',['卸行李开始', '卸货物开始'])
        elif "清洁作业开始时间" in selected_options:
            cal("清洁作业开始时间",dataf, 2, 0, 'KS', -1, 0, ['近机位下客结束', '远机位下客结束'], '清洁开始')
        elif "客舱清洁完成时间" in selected_options:
            cal("客舱清洁完成时间",dataf,1,0,0,1,0,'飞机入位机务到位','目标离港时间')
        elif "污水操作完成时间" in selected_options:
            cal("污水操作完成时间",dataf,1,0,0,1,0,'污水车拔管','目标离港时间')
        elif "清水操作完成时间" in selected_options:
            cal("清水操作完成时间",dataf,1,0,0,1,0,'清水车拔管','目标离港时间')
        # id20
        elif "餐食及机供品配供完成时间" in selected_options:
            cal("餐食及机供品配供完成时间",dataf,1,0,0,1,0,'配餐完成','目标离港时间')
        elif "非载客航油加注完成时间" in selected_options:
            cal_jiayou("非载客航油加注完成时间",dataf,0,'加油完成','目标离港时间')
        elif "载客航油加注完成时间" in selected_options:
            cal_jiayou("载客航油加注完成时间",dataf,1,'加油完成','目标离港时间')
        elif "机组到位时间-F" in selected_options:
            cal("机组到位时间-F",dataf,1,'F',0,1,0,'首名机组到机位','目标离港时间')
        elif "机组到位时间-其他" in selected_options:
            cal("机组到位时间-其他",dataf,1,'AE',0,1,0,'首名机组到机位','目标离港时间')
        # id25
        elif "近机位登机口开放时间-F" in selected_options:
            cal_djk("近机位登机口开放时间-F",dataf,'近','F','登机口开放','目标离港时间')
        elif "近机位登机口开放时间-其他" in selected_options:
            cal_djk("近机位登机口开放时间-其他",dataf,'近','AE','登机口开放','目标离港时间')
        elif "远机位登机口开放时间" in selected_options:
            cal_djk("远机位登机口开放时间",dataf,'远',0,'登机口开放','目标离港时间')
        elif "登机口关闭时间" in selected_options:
            cal("登机口关闭时间",dataf,1,0,0,1,0,'登机口关闭','目标离港时间')
        elif "行李装载开始时间" in selected_options:
            cal("行李装载开始时间",dataf,1,0,0,1,0,'装行李开始','目标离港时间')
        # id30
        elif "货邮、行李装载完成时间" in selected_options:
            cal("货邮、行李装载完成时间",dataf,1,0,0,1,0,'装载结束','目标离港时间')
        elif "首辆摆渡车到达登机口时间-ABC" in selected_options:
            cal("首辆摆渡车到达登机口时间-ABC",dataf,1,'ABC',0,1,0,'首辆摆渡车到达登机口','目标离港时间')
        elif "首辆摆渡车到达登机口时间-DE" in selected_options:
            cal("首辆摆渡车到达登机口时间-DE",dataf,1,'DE',0,1,0,'首辆摆渡车到达登机口','目标离港时间')
        elif "首辆摆渡车到达登机口时间-F" in selected_options:
            cal("首辆摆渡车到达登机口时间-F",dataf,1,'F',0,1,0,'首辆摆渡车到达登机口','目标离港时间')
        elif "出港最后一辆摆渡车到达远机位时间" in selected_options:
            cal("出港最后一辆摆渡车到达远机位时间",dataf,1,0,0,1,0,'最后一辆摆渡车到机位','目标离港时间')
        # id35
        elif "客舱门关闭完成时间" in selected_options:
            cal("客舱门关闭完成时间",dataf,1,0,0,1,0,'关客门','目标离港时间')
        elif "货舱门关闭完成时间" in selected_options:
            cal("货舱门关闭完成时间",dataf,1,0,0,1,0,'关货门','目标离港时间')
        elif "客舱门关闭与最后一个廊桥撤离的衔接" in selected_options:
            cal("客舱门关闭与最后一个廊桥撤离的衔接",dataf,2,0,'JS',-1,0,'关客门',['桥1撤离结束','桥2撤离结束','桥3撤离结束'])
        elif "单桥撤离作业时间" in selected_options:
            cal_shu("单桥撤离作业时间",dataf, 1, '廊桥数量', ['桥1撤离开始', '桥2撤离开始', '桥3撤离开始'],
                    ['桥1撤离结束', '桥2撤离结束', '桥3撤离结束'])
        elif "双桥撤离作业时间" in selected_options:
            cal_shu("双桥撤离作业时间",dataf, 2, '廊桥数量', ['桥1撤离开始', '桥2撤离开始', '桥3撤离开始'],
                    ['桥1撤离结束', '桥2撤离结束', '桥3撤离结束'])
        # id40
        elif "三桥撤离作业时间" in selected_options:
           cal_shu("三桥撤离作业时间",dataf,3,'廊桥数量',['桥1撤离开始','桥2撤离开始','桥3撤离开始'],['桥1撤离结束','桥2撤离结束','桥3撤离结束'])
        elif "客舱门关闭与最后一辆客梯车撤离的衔接" in selected_options:
            cal("客舱门关闭与最后一辆客梯车撤离的衔接",dataf, 2, 0, 'JS', -1, 0, '关客门',
                ['车1撤离结束', '车2撤离结束', '车3撤离结束'])
        elif "单客梯车撤离操作时间" in selected_options:
            cal_shu("单客梯车撤离操作时间",dataf, 1, '客梯车数量', ['车1撤离开始', '车2撤离开始', '车3撤离开始'],
                    ['车1撤离结束', '车2撤离结束', '车3撤离结束'])
        elif "多客梯车撤离操作时间" in selected_options:
            cal_shu("多客梯车撤离操作时间",dataf, 2, '客梯车数量', ['车1撤离开始', '车2撤离开始', '车3撤离开始'],
                    ['车1撤离结束', '车2撤离结束', '车3撤离结束'])
        elif "牵引车、机务、拖把到位时间" in selected_options:
            cal("牵引车、机务、拖把到位时间",dataf,2,0,'KS',1,0,['牵引车到位', '拖把到位', '飞机推出机务到位'],'TSAT',1)
        # id45
        elif "牵引车对接操作时间" in selected_options:
            cal("牵引车对接操作时间",dataf,1,0,0,-1,1,'牵引车对接开始','牵引车对接结束')
        elif "轮挡、反光锥形标志物撤离操作时间-ABC" in selected_options:
            cal("轮挡、反光锥形标志物撤离操作时间-ABC",dataf, 2, 'ABC', 'ALL', -1, 1, ['撤轮挡开始', '撤反光锥开始'], ['撤轮挡结束', '撤反光锥结束'])
        elif "轮挡、反光锥形标志物撤离操作时间-DEF" in selected_options:
            cal("轮挡、反光锥形标志物撤离操作时间-DEF",dataf, 2, 'DEF', 'ALL', -1, 1, ['撤轮挡开始', '撤反光锥开始'], ['撤轮挡结束', '撤反光锥结束'])
        elif "关舱门至首次RDY时间" in selected_options:
            cal("关舱门至首次RDY时间",dataf,1,0,0,-1,0,'关舱门','首次RDY')
        elif "接到指令到航空器开始推离机位时间(未对接)" in selected_options:
            cal_tc("接到指令到航空器开始推离机位时间(未对接)",dataf,0,'防撞灯闪烁','推出')
        # id50
        elif "接到指令到航空器开始推离机位时间(已对接)" in selected_options:
            cal_tc("接到指令到航空器开始推离机位时间(已对接)",dataf,1,'防撞灯闪烁','推出')
        elif "快速过站旅客下机-C" in selected_options:
            cal_ksgz("快速过站旅客下机-C",dataf,2,'ABC','JS',-1,1,'开客门',['近机位下客结束','远机位下客结束'])
        elif "快速过站旅客下机-E" in selected_options:
            cal_ksgz("快速过站旅客下机-E",dataf,2,'DEF','JS',-1,1,'开客门',['近机位下客结束','远机位下客结束'])
        elif "快速过站配餐-C" in selected_options:
            cal_ksgz("快速过站配餐-C",dataf,2,'ABC','KS',-1,1,['餐车1对接','餐车2对接','餐车3对接','餐车4对接'],'配餐完成')
        elif "快速过站配餐-E" in selected_options:
            cal_ksgz("快速过站配餐-E",dataf,2,'DEF','KS',-1,1,['餐车1对接','餐车2对接','餐车3对接','餐车4对接'],'配餐完成')
        # id55
        elif "快速过站清洁-C" in selected_options:
            cal_ksgz("快速过站清洁-C",dataf,1,'ABC',0,-1,1,'清洁开始','清洁完成')
        elif "快速过站清洁-E" in selected_options:
            cal_ksgz("快速过站清洁-E",dataf,1,'DEF',0,-1,1,'清洁开始','清洁完成')
        elif "快速过站加油-C" in selected_options:
            cal_ksgz("快速过站加油-C",dataf,1,'ABC',0,-1,1,'加油开始','加油完成')
        elif "快速过站加油-E" in selected_options:
            cal_ksgz("快速过站加油-E",dataf,1,'DEF',0,-1,1,'加油开始','加油完成')
        elif "快速过站旅客登机-C" in selected_options:
            cal_ksgz("快速过站旅客登机-C", dataf, 2, 'ABC', 'ALL', -1, 1, ['近机位登机开始', '远机位登机开始'], ['近机位登机结束', '远机位登机结束'])
        # id60
        elif "快速过站旅客登机-E" in selected_options:
            cal_ksgz("快速过站旅客登机-E", dataf, 2, 'DEF', 'ALL', -1, 1, ['近机位登机开始', '远机位登机开始'], ['近机位登机结束', '远机位登机结束'])
        elif "快速过站客舱清洁完成时间_下客结束-ABC" in selected_options:
            cal_ksgz("快速过站客舱清洁完成时间_下客结束-ABC",dataf,2,'ABC','KS',-1,0,['近机位下客结束','远机位下客结束'],'清洁完成')
        elif "快速过站客舱清洁完成时间_下客结束-DEF" in selected_options:
            cal_ksgz("快速过站客舱清洁完成时间_下客结束-DEF",dataf,2,'DEF','KS',-1,0,['近机位下客结束','远机位下客结束'],'清洁完成')
        elif "快速过站客舱清洁完成时间_上轮挡-ABC" in selected_options:
            cal_ksgz("快速过站客舱清洁完成时间_上轮挡-ABC",dataf,1,'ABC',0,-1,0,'上轮挡开始','清洁完成')
        elif "快速过站客舱清洁完成时间_上轮挡-DEF" in selected_options:
            cal_ksgz("快速过站客舱清洁完成时间_上轮挡-DEF",dataf,1,'DEF',0,-1,0,'上轮挡开始','清洁完成')
        # id65
        elif "快速过站配餐完成时间_下客结束-ABC" in selected_options:
            cal_ksgz("快速过站配餐完成时间_下客结束-ABC",dataf,2,'ABC','KS',-1,0,['近机位下客结束','远机位下客结束'],'配餐完成')
        elif "快速过站配餐完成时间_下客结束-DEF" in selected_options:
            cal_ksgz("快速过站配餐完成时间_下客结束-DEF",dataf,2,'DEF','KS',-1,0, ['近机位下客结束', '远机位下客结束'], '配餐完成')
        elif "快速过站配餐完成时间_上轮挡-ABC" in selected_options:
            cal_ksgz("快速过站配餐完成时间_上轮挡-ABC",dataf,1,'ABC',0,-1,0,'上轮挡开始','配餐完成')
        elif "快速过站配餐完成时间_上轮挡-DEF" in selected_options:
            cal_ksgz("快速过站配餐完成时间_上轮挡-DEF",dataf,1,'DEF',0,-1,0,'上轮挡开始','配餐完成')
        elif "快速过站登机口开放时间_近机位-ABC" in selected_options:
            cal_ksgz("快速过站登机口开放时间_近机位-ABC", dataf, 1, 'ABC', 0, -1, 0, '开客门', '登机口开放', 0, '近')
        # id70
        elif "快速过站登机口开放时间_近机位-DEF" in selected_options:
            cal_ksgz("快速过站登机口开放时间_近机位-DEF", dataf, 1, 'DEF', 0, -1, 0, '开客门', '登机口开放', 0, '近')
        elif "快速过站登机口开放时间_远机位-ABC" in selected_options:
            cal_ksgz("快速过站登机口开放时间_远机位-ABC", dataf, 1, 'ABC', 0, -1, 0, '开客门', '登机口开放', 0, '远')
        elif "快速过站登机口开放时间_远机位-DEF" in selected_options:
            cal_ksgz("快速过站登机口开放时间_远机位-DEF", dataf, 1, 'DEF', 0, -1, 0, '开客门', '登机口开放', 0, '远')

        else:
            messagebox.showinfo("提示", "未选择计算指标，请重试。")
            return
    except Exception as e:
        messagebox.showerror("错误", f"计算时出现错误: {str(e)}")
        return
    if result_df.empty:
        return

    #运行
    try:
        name = result_df.iloc[0, 0]
        plot_window = tk.Toplevel(root)
        plot_window.title(f"计算结果_{name}")
        # 调用函数创建Matplotlib图形并嵌入Tkinter窗口
        create_plot(result_df, plot_window)
        #result_df.to_csv(output_file_path, encoding='gbk', index=False)
    except Exception as e:
        messagebox.showerror("错误", f"画图时出现错误: {str(e)}")
        return

def process_data():
    # 获取用户输入的文件路径
    file_path = input_path_entry.get()

# try:
    # 检查是否选择了导入路径
    if not file_path:
        messagebox.showinfo("提示", "未选择导入路径，请重试。")
        return
    try:
        dataf = pd.read_csv(file_path, header=0, encoding='gbk', na_filter=False)
    except:
        messagebox.showinfo("错误", "导入文件异常，请检查文件后再试。")
        return
    # 获取用户输入的列名
    col_name_1 = qx_col1_entry.get()
    col_name_2 = qx_col2_entry.get()
    lower_threshold = float(qx_lower_threshold_entry.get())
    upper_threshold = float(qx_upper_threshold_entry.get())

    # 变量重置
    Y = []
    D = []
    error = 0
    T = 0
    result_text.delete('1.0', tk.END)

    # 遍历数据框
    for i in range(0, len(dataf)):
        if not pd.isna(dataf.loc[i, col_name_1]) and not len(dataf.loc[i, col_name_1]) == 0:
            if not pd.isna(dataf.loc[i, col_name_2]) and not len(dataf.loc[i, col_name_2]) == 0:
                if dataf.loc[i, col_name_1] == 'T':
                    T += 1
                elif dataf.loc[i, col_name_2] == 'T':
                    T += 1
                else:
                    try:
                        a = (ct(dataf.loc[i, col_name_2]) - ct(dataf.loc[i, col_name_1]))
                    except:
                        result_text.insert(tk.END, f'第{i+2}行结果异常！请检查！\n')
                        continue
                    if a < lower_threshold or a > upper_threshold:
                        result_text.insert(tk.END, f'第{i+2}行结果异常！请检查！\n')
                        error += 1
                    Y.append(a)
                    if a > 0:
                        D.append(a)

    # 显示错误信息
    if error > 0:
        result_text.insert(tk.END, f"处理完成，共发现{error}行错误\n")
        return

    # 显示处理结果
    result_text.insert(tk.END, f"处理完成，未发现错误。 ")
    return

# except Exception as e:
#     result_text.insert(tk.END, f"发生异常：{str(e)}\n")

def process_user():
    try:
        countcsv = 0
        input_file_path = input_path_entry.get()
        if not input_file_path:
            messagebox.showinfo("提示", "未选择导入路径，请重试。")
            return
        output_file_path = output_path_entry.get()
        if not output_file_path:
            messagebox.showinfo("提示", "未选择导入路径，请重试。")
            return
        try:
            dataf = pd.read_csv(input_file_path, header=0, encoding='gbk')
        except:
            messagebox.showinfo("错误", "导入文件异常，请检查文件后再试。")
            return

        name = col1_entry.get()
        start = col2_entry.get()
        end = col3_entry.get()
        mode = col4_entry.get()
        low1 = lower_threshold1_entry.get()
        up1 = upper_threshold1_entry.get()
        low2 = int(lower_threshold2_entry.get())
        up2 = int(upper_threshold2_entry.get())

        # 变量重置
        Y = []
        D = []
        T = 0
        # 遍历数据框
        for i in range(0, len(dataf)):
            if not pd.isna(dataf.loc[i, start]):
                if not pd.isna(dataf.loc[i, end]):
                    if dataf.loc[i, start] == 'T' or dataf.loc[i, end] == 'T':
                        T += 1
                    else:
                        a = (ct(dataf.loc[i, end]) - ct(dataf.loc[i, start]))
                        if a < -1380:
                            a += 1440
                        if int(low1) <= a <= int(up1):
                            Y.append(a)
                        if a > 0:
                            D.append(a)
        total(Y, low2, up2, name, T, 0)
        if mode == '协同指标驱动类':
            jf(Y, 1, 0)
            perc(D, 1, 0)
        elif mode in ['前后环节衔接类','持续时间类']:
            jf(Y, 0, 0)
            perc(D, 1, 0)
        else:
            messagebox.showinfo("错误", "指标类型输入有误！请检查！")
            return

        # 保存csv文件
        try:
            result_df.to_csv(output_file_path, encoding='gbk', index=False)
        except Exception as e:
            # 如果保存失败，尝试另存为新文件
            try:
                # 获取文件名和路径
                file_name, file_extension = os.path.splitext(output_file_path)
                new_output_file_path = f"{file_name}_1{file_extension}"
                result_df.to_csv(new_output_file_path, encoding='gbk', index=False)
                messagebox.showinfo("错误",
                                    f"保存文件时出现错误: {str(e)}\n文件保存到新路径: {new_output_file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"自定义计算时出现错误: {str(e)}")

        # 显示成功消息
        messagebox.showinfo("成功", "计算完成！文件已保存！")

    except Exception as e:
        # 如果出现异常，显示错误消息
        messagebox.showerror("错误", f"发生错误：{str(e)}，请重试。")

def gettime(data,period,i,mode):  # 用于获取节点的开始时间或完成时间
    # 未考虑数据中含0的情况
    ary = []
    get_stime = None  # 设置默认值
    get_etime = None  # 设置默认值
    for name in period:
        if data.loc[i, name] != '':
            ary.append(data.loc[i, name])
    if ary:
        get_stime = min(ary)
        get_etime = max(ary)
    if mode == 0:
        return get_stime
    elif mode == 1:
        return get_etime

def caltime(data,i,start,end,mode,mode1=0):
    # A是两个单指标，B为都是多指标，D为其中有一个为多指标
    if mode == 'A':
        try:
            if data.loc[i, end] == 'T' or data.loc[i, start] == 'T':
                return 'Y'  #读取是否存在T（提前完成），若有则直接返回T，对应程序中的满足
            time = ct(data.loc[i, end]) - ct(data.loc[i, start])
            if time == 0 and mode1 == 1:
                time += 1
            if time <= -1000:
                time += 1440
            return time
        except:
            return ''
    if mode == 'B' or mode == 'D':
        try:
            time = ct(gettime(data,end,i,1)) - ct(gettime(data,start,i,0))
            if time == 0 and mode1 == 1:
                time += 1
            if time <= -1000:
                time += 1440
            return time
        except:
            return ''

def ins():  # 用于调整输入数，目前无实用功能
    return

def readcsv():
    input_file_path = input_path_entry.get()
    if not input_file_path:
        messagebox.showinfo("提示", "未选择导入路径，请重试。")
        return
    # output_file_path = output_path_entry.get()
    # if not output_file_path:
    #     messagebox.showinfo("提示", "未选择导入路径，请重试。")
    #     return
    try:
        dataf_1 = pd.read_csv(input_file_path, header=0, encoding='gbk')
    except:
        messagebox.showinfo("错误", "导入文件异常，请检查文件后再试。")
        return

    try:
        rownum = int(tab4_col1b_entry.get())-1
    except:
        messagebox.showinfo("错误", "目标航班序号未填写！\n提示：若只有一条数据，填写1即可。")
        return
    # A类指标
    c1r1 = caltime(dataf_1,rownum,'拖曳到位','目标离港时间','A')
    c1r2 = caltime(dataf_1,rownum,'引导车到位','ELDT','A')
    c1r3 = caltime(dataf_1,rownum,'飞机入位机务到位','上轮挡开始','A')
    c1r4 = caltime(dataf_1,rownum,'客梯车到位','上轮挡开始','A')
    c1r5 = caltime(dataf_1,rownum,'首辆摆渡车到机位','上轮挡开始','A')
    c1r6 = caltime(dataf_1, rownum, '地服到位', '上轮挡开始', 'A')
    c1r7 = caltime(dataf_1, rownum, '装卸人员到位', '上轮挡开始', 'A')
    c1r8 = caltime(dataf_1, rownum, '清洁人员到位', '旅客下机完毕', 'A')
    c1r9 = caltime(dataf_1, rownum, '首名机组到机位', '目标离港时间', 'A')
    c1r10 = caltime(dataf_1, rownum, '首辆摆渡车到达登机口', '目标离港时间', 'A')
    c1r11 = caltime(dataf_1, rownum, '最后一辆摆渡车到机位', '目标离港时间', 'A')
    c1r12 = caltime(dataf_1, rownum, ['TSAT'], ['牵引车到位', '拖把到位', '飞机推出机务到位'], 'D')# 节点倒过来了，输入时需输入相反数
    # B类指标
    c1r13 = caltime(dataf_1, rownum, '登机口开放', '目标离港时间', 'A')
    c1r14 = caltime(dataf_1, rownum, '装行李开始', '目标离港时间', 'A')
    c1r15 = caltime(dataf_1, rownum, '通知翻找行李', '目标离港时间', 'A')
    c1r16 = caltime(dataf_1, rownum, '实挑实捡行李', '目标离港时间', 'A')

    # C类指标
    c2r1 = caltime(dataf_1, rownum, ['上轮挡开始','摆反光锥开始'], ['上轮挡结束','摆反光锥结束'], 'B',1)
    c2r2 = caltime(dataf_1, rownum, ['桥1对接开始','桥2对接开始','桥3对接开始','客梯车1对接开始','客梯车2对接开始','客梯车3对接开始'],
                   ['桥1对接结束','桥2对接结束','桥3对接结束','客梯车1对接结束','客梯车2对接结束','客梯车3对接结束'], 'B',1)
    if pd.isna(dataf_1.loc[rownum, '开客门操作时间']):
        c2r3 = ''
    else: c2r3 = int(dataf_1.loc[rownum, '开客门操作时间'])
    if pd.isna(dataf_1.loc[rownum, '开客门操作时间']):
        c2r4 = ''
    else: c2r4 = int(dataf_1.loc[rownum, '关客门操作时间'])
    if pd.isna(dataf_1.loc[rownum, '开客门操作时间']):
        c2r5 = ''
    else: c2r5 = int(dataf_1.loc[rownum, '关货门操作时间'])
    c2r6 = caltime(dataf_1, rownum, ['桥1撤离开始', '桥2撤离开始', '桥3撤离开始', '车1撤离开始', '车2撤离开始', '车3撤离开始'],
                   ['桥1撤离结束', '桥2撤离结束', '桥3撤离结束', '车1撤离结束', '车2撤离结束', '车3撤离结束'], 'B',1)
    c2r7 = caltime(dataf_1, rownum, '牵引车对接开始', '牵引车对接结束', 'A',1)
    c2r8 = caltime(dataf_1, rownum, ['撤轮挡开始', '撤反光锥开始'], ['撤轮挡结束', '撤反光锥结束'], 'B',1)
    # D类指标
    c2r9 = caltime(dataf_1, rownum, '申请拖曳时间', '目标离港时间', 'A')
    c2r10 = caltime(dataf_1, rownum, '廊桥检查及准备工作完成', '上轮挡开始', 'A')
    c2r12 = caltime(dataf_1, rownum, '清洁完成', '目标离港时间', 'A')

    c2r13 = caltime(dataf_1, rownum, '清水车拔管', '目标离港时间', 'A')
    c2r14 = caltime(dataf_1, rownum, '污水车拔管', '目标离港时间', 'A')
    c2r15 = caltime(dataf_1, rownum, '配餐完成', '目标离港时间', 'A')
    c2r16 = caltime(dataf_1, rownum, '加油完成', '目标离港时间', 'A')

    c3r1 = caltime(dataf_1, rownum, '登机口关闭', '目标离港时间', 'A')
    c3r2 = caltime(dataf_1, rownum, '舱单上传完成', '目标离港时间', 'A')
    c3r4 = caltime(dataf_1, rownum, '关客门', '目标离港时间', 'A')
    c3r5 = caltime(dataf_1, rownum, '关货门', '目标离港时间', 'A')
    c3r6 = caltime(dataf_1, rownum, '引导车通报引导信息', 'TSAT', 'A')
    # E类指标
    c3r7 = caltime(dataf_1, rownum, ['给出对接手势'], ['桥1对接开始','桥2对接开始','桥3对接开始','客梯车1对接开始','客梯车2对接开始','客梯车3对接开始'], 'D',1)
    c3r8 = caltime(dataf_1, rownum, ['开客门'],['桥1对接结束','桥2对接结束','桥3对接结束'
        ,'客梯车1对接结束','客梯车2对接结束','客梯车3对接结束'], 'D',1)  # 节点倒过来了，输入时需输入相反数
    c3r9 = caltime(dataf_1, rownum, '开货门', '卸行李开始', 'A',1)
    c3r10 = caltime(dataf_1, rownum, '旅客下机完毕', '清洁开始', 'A',1)
    c3r11 = caltime(dataf_1, rownum, ['关客门'], ['桥1撤离结束', '桥2撤离结束', '桥3撤离结束', '车1撤离结束', '车2撤离结束', '车3撤离结束'], 'D',1)
    c3r12 = caltime(dataf_1, rownum, ['首次RDY'], ['关客门', '关货门'], 'D',1)  # 节点倒过来了，输入时需输入相反数
    c3r13 = caltime(dataf_1, rownum, '防撞灯闪烁', '推出', 'A',1)
    c3r14 = caltime(dataf_1, rownum, '出港引导车接到指令', '出港引导车到位', 'A',1)

    # F类指标
    c4F1 = caltime(dataf_1, rownum, 'STD', 'ATOT', 'A', 1)
    c4F2 = caltime(dataf_1, rownum, 'COBT', '撤轮挡结束', 'A', 1)
    c4F3 = caltime(dataf_1, rownum, 'CTOT', 'ATOT', 'A', 1)
    c4F4 = caltime(dataf_1, rownum, 'ALDT', '上轮挡开始', 'A', 1)
    c4F5 = caltime(dataf_1, rownum, '撤轮挡结束', 'ATOT', 'A', 1)
    c4F6 = caltime(dataf_1, rownum, 'STD', 'ATOT', 'A', 1)

    try:
        if caltime(dataf_1, rownum, 'STA', '上轮挡开始', 'A', 1) <= 0:
            c4F7 = '否'
        elif caltime(dataf_1, rownum, 'STA', '上轮挡开始', 'A', 1) > 0:
            c4F7 = '是'
        else: c4F7 = ''
    except: c4F7 = ''

    #额外信息读取
    if pd.isna(dataf_1.loc[rownum, '进港近远机位']):
        c4r1 = ''
    else: c4r1 = dataf_1.loc[rownum, '进港近远机位']
    if pd.isna(dataf_1.loc[rownum, '机型大类']):
        c4r2 = ''
    else: c4r2 = dataf_1.loc[rownum, '机型大类']
    try:
        if dataf_1.loc[rownum, '是否加餐'] == 1:
            c4r3 = '是'
        elif dataf_1.loc[rownum, '是否加餐'] == 0:
            c4r3 = '否'
        else: c4r3 = '否'
    except: c4r3 = '否'
    try:
        if dataf_1.loc[rownum, '是否载客加油'] == 1:
            c4r4 = '是'
        elif dataf_1.loc[rownum, '是否载客加油'] == 0:
            c4r4 = '否'
        else: c4r4 = ''
    except: c4r4 = ''
    try:
        if dataf_1.loc[rownum, '牵引车对接结束'] > dataf_1.loc[rownum, '防撞灯闪烁']:
            c4r5 = '否'
        elif dataf_1.loc[rownum, '牵引车对接结束'] <= dataf_1.loc[rownum, '防撞灯闪烁']:
            c4r5 = '是'
        else: c4r5 = ''
    except: c4r5 = ''
    if pd.isna(dataf_1.loc[rownum, '廊桥数量']) and pd.isna(dataf_1.loc[rownum, '客梯车数量']):
        c4r6 = ''
    elif pd.isna(dataf_1.loc[rownum, '廊桥数量']) or dataf_1.loc[rownum, '廊桥数量'] == '':
        c4r6 = int(dataf_1.loc[rownum, '客梯车数量'])
    elif pd.isna(dataf_1.loc[rownum, '客梯车数量']):
        c4r6 = int(dataf_1.loc[rownum, '廊桥数量'])
    else:
        c4r6 = int(dataf_1.loc[rownum, '廊桥数量'])

# 在tab4中插入计算值
    tab4_col1_entry.delete(0, tk.END)
    tab4_col1_entry.insert(0, c1r1)
    tab4_col2_entry.delete(0, tk.END)
    tab4_col2_entry.insert(0, c1r2)
    tab4_col3_entry.delete(0, tk.END)
    tab4_col3_entry.insert(0, c1r3)
    tab4_col4_entry.delete(0, tk.END)
    tab4_col4_entry.insert(0, c1r4)
    tab4_col5_entry.delete(0, tk.END)
    tab4_col5_entry.insert(0, c1r5)
    tab4_col6_entry.delete(0, tk.END)
    tab4_col6_entry.insert(0, c1r6)
    tab4_col7_entry.delete(0, tk.END)
    tab4_col7_entry.insert(0, c1r7)
    tab4_col8_entry.delete(0, tk.END)
    tab4_col8_entry.insert(0, c1r8)
    tab4_col9_entry.delete(0, tk.END)
    tab4_col9_entry.insert(0, c1r9)
    tab4_cola_entry.delete(0, tk.END)
    tab4_cola_entry.insert(0, c1r10)
    tab4_colb_entry.delete(0, tk.END)
    tab4_colb_entry.insert(0, c1r11)
    tab4_colc_entry.delete(0, tk.END)
    try:
        tab4_colc_entry.insert(0, str(-int(c1r12)))
    except:
        tab4_colc_entry.insert(0, '')
    tab4_cold_entry.delete(0, tk.END)
    tab4_cold_entry.insert(0, c1r13)
    tab4_cole_entry.delete(0, tk.END)
    tab4_cole_entry.insert(0, c1r14)
    tab4_colf_entry.delete(0, tk.END)
    tab4_colf_entry.insert(0, c1r15)
    tab4_colg_entry.delete(0, tk.END)
    tab4_colg_entry.insert(0, c1r16)
    tab4_c2r1_entry.delete(0, tk.END)
    tab4_c2r1_entry.insert(0, c2r1)
    tab4_c2r2_entry.delete(0, tk.END)
    tab4_c2r2_entry.insert(0, c2r2)
    tab4_c2r3_entry.delete(0, tk.END)
    tab4_c2r3_entry.insert(0, c2r3)
    tab4_c2r4_entry.delete(0, tk.END)
    tab4_c2r4_entry.insert(0, c2r4)
    tab4_c2r5_entry.delete(0, tk.END)
    tab4_c2r5_entry.insert(0, c2r5)
    tab4_c2r6_entry.delete(0, tk.END)
    tab4_c2r6_entry.insert(0, c2r6)
    tab4_c2r7_entry.delete(0, tk.END)
    tab4_c2r7_entry.insert(0, c2r7)
    tab4_c2r8_entry.delete(0, tk.END)
    tab4_c2r8_entry.insert(0, c2r8)
    tab4_c2r9_entry.delete(0, tk.END)
    tab4_c2r9_entry.insert(0, c2r9)
    tab4_c2r10_entry.delete(0, tk.END)
    tab4_c2r10_entry.insert(0, c2r10)
    tab4_c2r12_entry.delete(0, tk.END)
    tab4_c2r12_entry.insert(0, c2r12)
    tab4_c2r13_entry.delete(0, tk.END)
    tab4_c2r13_entry.insert(0, c2r13)
    tab4_c2r14_entry.delete(0, tk.END)
    tab4_c2r14_entry.insert(0, c2r14)
    tab4_c2r15_entry.delete(0, tk.END)
    tab4_c2r15_entry.insert(0, c2r15)
    tab4_c2r16_entry.delete(0, tk.END)
    tab4_c2r16_entry.insert(0, c2r16)
    tab4_c3r1_entry.delete(0, tk.END)
    tab4_c3r1_entry.insert(0, c3r1)
    tab4_c3r2_entry.delete(0, tk.END)
    tab4_c3r2_entry.insert(0, c3r2)
    tab4_c3r4_entry.delete(0, tk.END)
    tab4_c3r4_entry.insert(0, c3r4)
    tab4_c3r5_entry.delete(0, tk.END)
    tab4_c3r5_entry.insert(0, c3r5)
    tab4_c3r6_entry.delete(0, tk.END)
    tab4_c3r6_entry.insert(0, c3r6)
    tab4_c3r7_entry.delete(0, tk.END)
    tab4_c3r7_entry.insert(0, c3r7)
    tab4_c3r8_entry.delete(0, tk.END)
    try:
        tab4_c3r8_entry.insert(0, str(-int(c3r8)))
    except:
        tab4_c3r8_entry.insert(0, '')
    tab4_c3r9_entry.delete(0, tk.END)
    tab4_c3r9_entry.insert(0, c3r9)
    tab4_c3r10_entry.delete(0, tk.END)
    tab4_c3r10_entry.insert(0, c3r10)
    tab4_c3r11_entry.delete(0, tk.END)
    tab4_c3r11_entry.insert(0, c3r11)
    tab4_c3r12_entry.delete(0, tk.END)
    try:
        tab4_c3r12_entry.insert(0, str(-int(c3r12)))
    except: tab4_c3r12_entry.insert(0, '')
    tab4_c3r13_entry.delete(0, tk.END)
    tab4_c3r13_entry.insert(0, c3r13)
    tab4_c3r14_entry.delete(0, tk.END)
    tab4_c3r14_entry.insert(0, c3r14)
    tab4_F1_entry.delete(0, tk.END)
    try:
        tab4_F1_entry.insert(0, str(c4F1-30))
    except:
        tab4_F1_entry.insert(0, '')
    tab4_F2_entry.delete(0, tk.END)
    tab4_F2_entry.insert(0, c4F2)
    tab4_F3_entry.delete(0, tk.END)
    tab4_F3_entry.insert(0, c4F3)
    tab4_F4_entry.delete(0, tk.END)
    tab4_F4_entry.insert(0, c4F4)
    tab4_F5_entry.delete(0, tk.END)
    tab4_F5_entry.insert(0, c4F5)
    tab4_F6_entry.delete(0, tk.END)
    if c4F7 == '是':
        tab4_F6_entry.insert(0, str(c4F6-40))
    elif c4F7 == '否':
        tab4_F6_entry.insert(0, str(c4F6-30))
    else:
        tab4_F6_entry.insert(0, '')
    tab4_F7_entry.delete(0, tk.END)
    tab4_F7_entry.insert(0, c4F7)

    tab4_c4r1_entry.delete(0, tk.END)
    tab4_c4r1_entry.insert(0, c4r1)
    tab4_c4r2_entry.delete(0, tk.END)
    tab4_c4r2_entry.insert(0, c4r2)
    tab4_c4r3_entry.delete(0, tk.END)
    tab4_c4r3_entry.insert(0, c4r3)
    tab4_c4r4_entry.delete(0, tk.END)
    tab4_c4r4_entry.insert(0, c4r4)
    tab4_c4r5_entry.delete(0, tk.END)
    tab4_c4r5_entry.insert(0, c4r5)
    tab4_c4r6_entry.delete(0, tk.END)
    tab4_c4r6_entry.insert(0, c4r6)

def cal_score():
    # 各指标的权重可更改
    # 改进方案，可以把standard改成读取形式，方便用户修改
    sum = 0
    jiwei = tab4_c4r1_entry.get()
    jixin = tab4_c4r2_entry.get()
    jiacan = tab4_c4r3_entry.get()
    zaikejiayou = tab4_c4r4_entry.get()
    shifouduijie = tab4_c4r5_entry.get()
    qcshumu = tab4_c4r6_entry.get()
    ## A类指标
    if jiwei == '近':
        if jixin == 'F':
            sum += cal_single(tab4_col1_entry, 120, 1, 'A', 0.2)
        else:
            sum += cal_single(tab4_col1_entry, 90, 1, 'A', 0.2)
        sum += cal_single(tab4_col2_entry, 0, 1, 'A', 0)
        sum += cal_single(tab4_col3_entry, 5, 1, 'A', 0.15)
        sum += cal_single(tab4_col6_entry, 5, 1, 'A', 0)
        sum += cal_single(tab4_col7_entry, 5, 1, 'A', 0)
        sum += cal_single(tab4_col8_entry, 0, 1, 'A', 0.15)
        if jixin == 'F':
            sum += cal_single(tab4_col9_entry, 70, 1, 'A', 0.25)
        else:
            sum += cal_single(tab4_col9_entry, 60, 1, 'A', 0.25)
        sum += cal_single(tab4_colc_entry, 10, 1, 'A', 0.25)
    elif jiwei == '远':
        if jixin == 'F':
            sum += cal_single(tab4_col1_entry, 120, 1, 'A', 0.12)
        else:
            sum += cal_single(tab4_col1_entry, 90, 1, 'A', 0.12)
        sum += cal_single(tab4_col2_entry, 0, 1, 'A', 0)
        sum += cal_single(tab4_col3_entry, 5, 1, 'A', 0.04)
        sum += cal_single(tab4_col4_entry, 5, 1, 'A', 0.04)
        sum += cal_single(tab4_col5_entry, 5, 1, 'A', 0.12)
        sum += cal_single(tab4_col6_entry, 5, 1, 'A', 0)
        sum += cal_single(tab4_col7_entry, 5, 1, 'A', 0)
        sum += cal_single(tab4_col8_entry, 0, 1, 'A', 0.04)
        if jixin == 'F':
            sum += cal_single(tab4_col9_entry, 70, 1, 'A', 0.2)
        else:
            sum += cal_single(tab4_col9_entry, 60, 1, 'A', 0.2)
        if jixin == 'F':
            sum += cal_single(tab4_cola_entry, 60, 1, 'A', 0.12)
        elif jixin == 'D' or jixin == 'E':
            sum += cal_single(tab4_cola_entry, 50, 1, 'A', 0.12)
        else:
            sum += cal_single(tab4_cola_entry, 45, 1, 'A', 0.12)
        sum += cal_single(tab4_colb_entry, 7, 1, 'A', 0.12)
        sum += cal_single(tab4_colc_entry, 10, 1, 'A', 0.20)
    else:
        messagebox.showerror("错误", "机位信息输入有误，请重新输入")
        return

    ## B类指标
    if jiwei == '近':
        if jixin == 'F':
            sum += cal_single(tab4_cold_entry, 40, 1, 'B', 0.25)
        else:
            sum += cal_single(tab4_cold_entry, 35, 1, 'B', 0.25)
    elif jiwei == '远':
        sum += cal_single(tab4_cold_entry, 45, 1, 'B', 0.25)
    else:
        messagebox.showerror("错误", "机位信息输入有误，请重新输入")
        return
    sum += cal_single(tab4_cole_entry, 20, 1, 'B', 0.25)
    if jixin == 'F':
        sum += cal_single(tab4_colf_entry, 25, 1, 'B', 0.25)
    elif jixin == 'D' or jixin == 'E':
        sum += cal_single(tab4_colf_entry, 20, 1, 'B', 0.25)
    else:
        sum += cal_single(tab4_colf_entry, 15, 1, 'B', 0.25)
    if jixin == 'E' or jixin == 'F':
        sum += cal_single(tab4_colg_entry, 15, 1, 'B', 0.25)
    else:
        sum += cal_single(tab4_colg_entry, 10, 1, 'B', 0.25)

    ## C类指标
    if jixin == 'D' or jixin == 'E' or jixin == 'F':
        sum += cal_single(tab4_c2r1_entry, 4, 2, 'C', 0)
    else:
        sum += cal_single(tab4_c2r1_entry, 3, 2, 'C', 0)
    if jiwei == '近':
        if qcshumu == '1':
            sum += cal_single(tab4_c2r2_entry, 2, 2, 'C', 0)
        elif qcshumu == '2':
            sum += cal_single(tab4_c2r2_entry, 4, 2, 'C', 0)
        elif qcshumu == '3':
            sum += cal_single(tab4_c2r2_entry, 8, 2, 'C', 0)
        else:
            sum += cal_single(tab4_c2r2_entry, 2, 2, 'C', 0)
    elif jiwei == '远':
        if qcshumu == '1':
            sum += cal_single(tab4_c2r2_entry, 2, 2, 'C', 0)
        elif int(qcshumu) > 1:
            sum += cal_single(tab4_c2r2_entry, 4, 2, 'C', 0)
        else:
            sum += cal_single(tab4_c2r2_entry, 2, 2, 'C', 0)
    else:
        messagebox.showerror("错误", "机位信息输入有误，请重新输入")
        return
    sum += cal_single(tab4_c2r3_entry, 1, 2, 'C', 0)
    sum += cal_single(tab4_c2r4_entry, 1, 2, 'C', 0)
    sum += cal_single(tab4_c2r5_entry, 2, 2, 'C', 0)
    if jiwei == '近':
        if qcshumu == '1':
            sum += cal_single(tab4_c2r6_entry, 2, 2, 'C', 0.5)
        elif qcshumu == '2':
            sum += cal_single(tab4_c2r6_entry, 4, 2, 'C', 0.5)
        elif qcshumu == '3':
            sum += cal_single(tab4_c2r6_entry, 6, 2, 'C', 0.5)
        else:
            sum += cal_single(tab4_c2r6_entry, 2, 2, 'C', 0.5)
    elif jiwei == '远':
        if qcshumu == '1':
            sum += cal_single(tab4_c2r6_entry, 2, 2, 'C', 0.5)
        elif int(qcshumu) > 1:
            sum += cal_single(tab4_c2r6_entry, 4, 2, 'C', 0.5)
        else:
            sum += cal_single(tab4_c2r6_entry, 2, 2, 'C', 0.5)
    else:
        messagebox.showerror("错误", "机位信息输入有误，请重新输入")
        return
    sum += cal_single(tab4_c2r7_entry, 3, 2, 'C', 0.5)
    if jixin == 'D' or jixin == 'E' or jixin == 'F':
        sum += cal_single(tab4_c2r8_entry, 4, 2, 'C', 0)
    else:
        sum += cal_single(tab4_c2r8_entry, 3, 2, 'C', 0)

    ## D类指标
    if jixin == 'E' or jixin == 'F':
        sum += cal_single(tab4_c2r9_entry, 150, 1, 'D', 0)
    else:
        sum += cal_single(tab4_c2r9_entry, 120, 1, 'D', 0)
    if jiwei == '近':
        if qcshumu == '1' or qcshumu == '2':
            sum += cal_single(tab4_c2r10_entry, 10, 1, 'D', 0)
        elif qcshumu == '3':
            sum += cal_single(tab4_c2r10_entry, 20, 1, 'D', 0)
    else:
        sum += 0
    sum += cal_single(tab4_c2r12_entry, 40, 1, 'D', 0.1)
    sum += cal_single(tab4_c2r13_entry, 20, 1, 'D', 0)
    sum += cal_single(tab4_c2r14_entry, 20, 1, 'D', 0)
    if jiacan == '是':
        sum += cal_single(tab4_c2r15_entry, 10, 1, 'D', 0.1)
    elif jiacan == '否':
        sum += cal_single(tab4_c2r15_entry, 40, 1, 'D', 0.1)
    else:
        sum += cal_single(tab4_c2r15_entry, 40, 1, 'D', 0.1)
    if zaikejiayou == '是':
        sum += cal_single(tab4_c2r16_entry, 10, 1, 'D', 0.1)
    elif zaikejiayou == '否':
        sum += cal_single(tab4_c2r16_entry, 40, 1, 'D', 0.1)
    else:
        sum += cal_single(tab4_c2r16_entry, 40, 1, 'D', 0.1)

    sum += cal_single(tab4_c3r1_entry, 10, 1, 'D', 0.1)
    sum += cal_single(tab4_c3r2_entry, 8, 1, 'D', 0.1)
    sum += cal_single(tab4_c3r4_entry, 5, 1, 'D', 0.15)
    sum += cal_single(tab4_c3r5_entry, 5, 1, 'D', 0.15)
    sum += cal_single(tab4_c3r6_entry, 10, 1, 'D', 0)

    ## E类指标
    sum += cal_single(tab4_c3r7_entry, 1, 2, 'E', 0)
    sum += cal_single(tab4_c3r8_entry, 1, 2, 'E', 0)
    if jixin == 'D' or jixin == 'E' or jixin == 'F':
        sum += cal_single(tab4_c3r9_entry, 3, 2, 'E', 0.18)
    else:
        sum += cal_single(tab4_c3r9_entry, 2, 2, 'E', 0.18)
    sum += cal_single(tab4_c3r10_entry, 2, 2, 'E', 0.14)
    if jiwei == '近':
        sum += cal_single(tab4_c3r11_entry, 3, 2, 'E', 0.18)
    elif jiwei =='远':
        sum += cal_single(tab4_c3r11_entry, 2, 2, 'E', 0.18)
    else:
        sum += 0
    sum += cal_single(tab4_c3r12_entry, 2, 2, 'E', 0.18)
    if shifouduijie == '是':
        sum += cal_single(tab4_c3r13_entry, 1, 2, 'E', 0.18)
    elif shifouduijie == '否':
        sum += cal_single(tab4_c3r13_entry, 3, 2, 'E', 0.18)
    else:
        sum += cal_single(tab4_c3r13_entry, 3, 2, 'E', 0.18)
    sum += cal_single(tab4_c3r14_entry, 10, 2, 'E', 0.14)

    ## F类指标
    sum += cal_single(tab4_F1_entry, 0, 2, 'F', 0.3)
    try:
        if int(tab4_F2_entry.get()) >= 0:
            sum += cal_single(tab4_F2_entry, 10, 2, 'F', 0.2)
        elif int(tab4_F2_entry.get()) < 0:
            sum += cal_single(tab4_F2_entry, -5, 1, 'F', 0.2)
        else:
            sum += 0
    except:
        sum += 0
    try:
        if int(tab4_F3_entry.get()) >= 0:
            sum += cal_single(tab4_F3_entry, 10, 2, 'F', 0.1)
        elif int(tab4_F3_entry.get()) < 0:
            sum += cal_single(tab4_F3_entry, -5, 1, 'F', 0.1)
        else:
            sum += 0
    except:
        sum += 0
    sum += cal_single(tab4_F4_entry, 12, 2, 'F', 0.1)
    # 指标若有三个打分标准，则分成两段，每段的权重为原权重/2
    sum += cal_single(tab4_F5_entry, 25, 2, 'F', 0.075)
    sum += cal_single(tab4_F5_entry, 30, 2, 'F', 0.075)
    sum += cal_single(tab4_F6_entry, 0, 2, 'F', 0.075)
    sum += cal_single(tab4_F6_entry, 5, 2, 'F', 0.075)

    score = round(sum * 100, 3)
    tab4_col1c_entry.delete(0, tk.END)
    tab4_col1c_entry.insert(0, str(score))
    return

def cal_single(entry, standard, mode, type, weight):
    # standard为标准阈值，mode为指标类型（1是高于阈值满足，2是低于阈值满足）
    # type为指标类别，weight为指标权重
    time = entry.get()
    try:
        time = int(time)
    except:
        time = time

    type_to_score = {'A': 0.1, 'B': 0.1, 'C': 0.05, 'D': 0.2, 'E': 0.15, 'F': 0.4}
    if type in type_to_score:
        score = type_to_score[type]

    else:
        return 0
    score = score * weight

    if time == '':
        return 0  # 输入为空时不算分
    elif time == 'Y':
        return score
    elif mode == 1 and time >= standard:
        return score
    elif mode == 2 and time <= standard:
        return score
    else:
        return 0

def custom_sort_key(item):
    order = ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'  # 定义排序规则
    first_letter = item[0] if item else ' '  # 获取元素的首字母，空字符串取空格
    second_letter = item[1] if len(item) > 1 else ' '  # 获取元素的第二个字母，空字符串取空格
    return order.index(first_letter) * len(order) + order.index(second_letter)

def read_airlines(filepath):  # 获取所有航空公司
    array = [" "]
    try:
        data = pd.read_csv(filepath, header=0, encoding='gbk')
    except:
        messagebox.showinfo("错误", "导入文件异常，请检查文件后再试。")
        return
    for i in range(0, len(data)):
        if not pd.isna(data.loc[i, '离港航班号']) and data.loc[i, '离港航班号'] != '':
            alname = data.loc[i, '离港航班号']
            alname = alname[:2]
        elif not pd.isna(data.loc[i, '进港航班号']) and data.loc[i, '进港航班号'] != '':
            alname = data.loc[i, '进港航班号']
            alname = alname[:2]
        else:
            alname = ' '
        if alname not in array:
            array.append(alname)
    array = sorted(array[0:], key=custom_sort_key)
    return array

def read_agent(filepath):  # 获取所有代理
    array = [" "]
    try:
        data = pd.read_csv(filepath, header=0, encoding='gbk')
    except:
        messagebox.showinfo("错误", "导入文件异常，请检查文件后再试。")
        return
    for i in range(0, len(data)):
        if not pd.isna(data.loc[i, '保障代理']) and data.loc[i, '保障代理'] != '':
            agname = data.loc[i, '保障代理']
        else:
            agname = ' '
        if agname not in array:
            array.append(agname)
    array = sorted(array[0:], key=custom_sort_key)
    return array

#机位的顺序可能要重新调一下
def read_stand(filepath):  # 获取所有机位
    array = [" "]
    try:
        data = pd.read_csv(filepath, header=0, encoding='gbk')
    except:
        messagebox.showinfo("错误", "导入文件异常，请检查文件后再试。")
        return
    for i in range(0, len(data)):
        if not pd.isna(data.loc[i, '停机位']) and data.loc[i, '停机位'] != '':
            sname = data.loc[i, '停机位']
        else:
            sname = ' '
        if sname not in array:
            array.append(sname)
    array = sorted(array[0:], key=custom_sort_key)
    return array

##############################################################################################
## 程序UI设计
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height - 100) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")

# 创建主UI窗口
root = tk.Tk()
root.title("保障环节计算 Ver1.10")

# 设置窗口背景颜色
root.configure(bg="#f0f0f0")

# 调用函数使窗口居中
root.state('zoomed')
# center_window(root, 550, 680)

# 创建一个标签和输入框用于导入路径
input_label = tk.Label(root, text="导入路径:")
input_label.grid(row=0, column=0, padx=1, pady=10, sticky=tk.E)
input_path_entry = tk.Entry(root, width=45)
input_path_entry.grid(row=0, column=1, padx=1, pady=10, sticky=tk.W)

# 创建选择导入路径的按钮
def browse_input_path():
    global airlines
    global agent
    global stand
    input_file_path = filedialog.askopenfilename(title="选择导入文件", filetypes=[("CSV文件", "*.csv")])
    input_path_entry.delete(0, tk.END)
    input_path_entry.insert(0, input_file_path)
    airlines = read_airlines(input_file_path)
    agent = read_agent(input_file_path)
    stand = read_stand(input_file_path)
    airlines_combobox['values'] = airlines  # 更新下拉框的值
    agent_combobox['values'] = agent  # 更新下拉框的值
    stand_combobox['values'] = stand  # 更新下拉框的值

airlines = [' ']
agent = [' ']
stand = [' ']
browse_input_button = tk.Button(root, text="选择导入文件", command=browse_input_path)
browse_input_button.place(x=660, y=21, anchor='w')

# 创建一个标签和输入框用于导出路径
output_label = tk.Label(root, text="导出路径:")
output_label.grid(row=1, column=0, padx=1, pady=10, sticky=tk.E)
output_path_entry = tk.Entry(root, width=45)
output_path_entry.grid(row=1, column=1, padx=1, pady=10, sticky=tk.W)

# 创建选择导出路径的按钮
def browse_output_path():
    output_file_path = filedialog.asksaveasfilename(title="选择导出文件", filetypes=[("CSV文件", "*.csv")])
    output_path_entry.delete(0, tk.END)
    output_path_entry.insert(0, output_file_path)

browse_output_button = tk.Button(root, text="选择导出路径", command=browse_output_path)
browse_output_button.place(x=660, y=65, anchor='w')

# 创建下拉框-航空公司
airlines_entry = tk.StringVar(value=" ")
airlines_label = tk.Label(root, text="航空公司:")
airlines_label.place(x=780, y=21, anchor='w')
airlines_combobox = ttk.Combobox(root, textvariable=airlines_entry, values=airlines, state="readonly",
                             width=10)
style = ttk.Style()
style.configure("TCombobox", padding=5, relief="flat", borderwidth=1)
airlines_combobox["style"] = "TCombobox"
airlines_combobox.place(x=850, y=21, anchor='w')

# 创建下拉框-代理
agent_entry = tk.StringVar(value=" ")
agent_label = tk.Label(root, text="代      理:")
agent_label.place(x=780, y=65, anchor='w')
agent_combobox = ttk.Combobox(root, textvariable=agent_entry, values=agent, state="readonly",
                             width=10)
style = ttk.Style()
style.configure("TCombobox", padding=5, relief="flat", borderwidth=1)
agent_combobox["style"] = "TCombobox"
agent_combobox.place(x=850, y=65, anchor='w')

# 创建下拉框-机位
stand_entry = tk.StringVar(value=" ")
stand_label = tk.Label(root, text="机      位:")
stand_label.place(x=970, y=21, anchor='w')
stand_combobox = ttk.Combobox(root, textvariable=stand_entry, values=stand, state="readonly",
                             width=10)
style = ttk.Style()
style.configure("TCombobox", padding=5, relief="flat", borderwidth=1)
stand_combobox["style"] = "TCombobox"
stand_combobox.place(x=1040, y=21, anchor='w')

# 创建下拉框-航班性质
flight_entry = tk.StringVar(value=" ")
flight_label = tk.Label(root, text="航班性质:")
flight_label.place(x=1160, y=21, anchor='w')
flight_combobox = ttk.Combobox(root, textvariable=stand_entry, values=[' ', '国内', '国际', '地区'], state="readonly",
                             width=10)
style = ttk.Style()
style.configure("TCombobox", padding=5, relief="flat", borderwidth=1)
flight_combobox["style"] = "TCombobox"
flight_combobox.place(x=1230, y=21, anchor='w')

# 创建下拉框-时间
time_label = tk.Label(root, text="时间范围:")
time_label.place(x=970, y=65, anchor='w')
time_entry_1 = tk.Entry(root, width=10)
time_entry_1.place(x=1040, y=65, anchor='w')
time_label_mid = tk.Label(root, text="——")
time_label_mid.place(x=1116, y=65, anchor='w')
time_entry_2 = tk.Entry(root, width=10)
time_entry_2.place(x=1150, y=65, anchor='w')

# 创建选项卡
notebook = ttk.Notebook(root)
notebook.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W, columnspan=4)

# 创建第一个选项卡
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="航班保障标准统计")

# 设置列权重，使每列的宽度相同
#tab1.columnconfigure(2, minsize=1)

input_label = tk.Label(tab1, text="计算指标:")
input_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

# 创建子选项卡
notebook1 = ttk.Notebook(tab1)
notebook1.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
#########################################################
# 创建第一个子选项卡
tab1_1 = ttk.Frame(notebook1)
notebook1.add(tab1_1, text="人员/车辆/设备到位")

#可滚动区域
checkbox_frame1 = ttk.Frame(tab1_1)
checkbox_frame1.grid(row=3, column=0, padx=10, pady=10, columnspan=4, sticky=tk.W)

# 创建一个Frame用于包装canvas1和scrollbar1
scroll_frame1 = ttk.Frame(checkbox_frame1, borderwidth=2, relief="solid")
scroll_frame1.pack(side="left", fill="both", expand=True)

canvas1 = tk.Canvas(scroll_frame1, height=250)
scrollbar1 = ttk.Scrollbar(scroll_frame1, orient="vertical", command=canvas1.yview)
scrollable_frame1 = ttk.Frame(canvas1)

scrollable_frame1.bind(
    "<Configure>",
    lambda e: canvas1.configure(scrollregion=canvas1.bbox("all"))
)

canvas1.create_window((0, 0), window=scrollable_frame1, anchor="nw")
canvas1.configure(yscrollcommand=scrollbar1.set)

canvas1.pack(side="left", fill="both", expand=True)
scrollbar1.pack(side="right", fill="y")

def on_enter(event):
    # 鼠标进入事件处理函数
    canvas1.bind_all("<MouseWheel>", on_mousewheel_1)

def on_leave(event):
    # 鼠标离开事件处理函数
    canvas1.unbind_all("<MouseWheel>")

# 绑定鼠标进入和离开事件
scrollable_frame1.bind("<Enter>", on_enter)
scrollable_frame1.bind("<Leave>", on_leave)

def on_mousewheel_1(event):
    # 鼠标滚轮事件处理函数
    # Delta为正表示向上滚动，为负表示向下滚动
    delta1 = -event.delta // 120
    canvas1.yview_scroll(delta1, "units")

# 绑定鼠标滚轮事件
canvas1.bind("<MouseWheel>", on_mousewheel_1)
# 将整个scroll_frame放入checkbox_frame
scroll_frame1.pack(side="left", fill="both", expand=True)

selected_option1 = tk.StringVar()

options1 = [
    "过站机务到位",
    "客梯车到达机位时间",
    "首辆摆渡车到达机位时间",
    "地服接机人员到位时间",
    "装卸人员及装卸设备到位时间",
    "机组到位时间-F",
    "机组到位时间-其他",
    "首辆摆渡车到达登机口时间-ABC",
    "首辆摆渡车到达登机口时间-DE",
    "首辆摆渡车到达登机口时间-F",
    "出港最后一辆摆渡车到达远机位时间",
    "牵引车、机务、拖把到位时间"
]

for index, option_text in enumerate(options1):
    radio_button = tk.Radiobutton(
        scrollable_frame1,
        text=option_text,
        variable=selected_option1,
        value=option_text,
        anchor='w',
        justify=tk.LEFT,
        wraplength=300
    )
    radio_button.grid(row=index, column=0, padx=10, pady=1, sticky=tk.W, columnspan=2)

selected_option1.set(None)
##############################################################
#########################################################3
# 创建第二个子选项卡
tab1_2 = ttk.Frame(notebook1)
notebook1.add(tab1_2, text="作业操作时间")

#可滚动区域
checkbox_frame_2 = ttk.Frame(tab1_2)
checkbox_frame_2.grid(row=3, column=0, padx=10, pady=10, columnspan=4, sticky=tk.W)

scroll_frame_2 = ttk.Frame(checkbox_frame_2, borderwidth=2, relief="solid")
scroll_frame_2.pack(side="left", fill="both", expand=True)

canvas_2 = tk.Canvas(scroll_frame_2, height=250)
scrollbar_2 = ttk.Scrollbar(scroll_frame_2, orient="vertical", command=canvas_2.yview)
scrollable_frame_2 = ttk.Frame(canvas_2)

scrollable_frame_2.bind(
    "<Configure>",
    lambda e: canvas_2.configure(scrollregion=canvas_2.bbox("all"))
)

canvas_2.create_window((0, 0), window=scrollable_frame_2, anchor="nw")
canvas_2.configure(yscrollcommand=scrollbar_2.set)

canvas_2.pack(side="left", fill="both", expand=True)
scrollbar_2.pack(side="right", fill="y")

def on_enter(event):
    # 鼠标进入事件处理函数
    canvas_2.bind_all("<MouseWheel>", on_mousewheel_2)

def on_leave(event):
    # 鼠标离开事件处理函数
    canvas_2.unbind_all("<MouseWheel>")

# 绑定鼠标进入和离开事件
scrollable_frame_2.bind("<Enter>", on_enter)
scrollable_frame_2.bind("<Leave>", on_leave)
def on_mousewheel_2(event):
    # 鼠标滚轮事件处理函数
    # Delta为正表示向上滚动，为负表示向下滚动
    delta_2 = -event.delta // 120
    canvas_2.yview_scroll(delta_2, "units")

# 绑定鼠标滚轮事件
canvas_2.bind("<MouseWheel>", on_mousewheel_2)

# 将整个scroll_frame放入checkbox_frame
scroll_frame_2.pack(side="left", fill="both", expand=True)

selected_option_2 = tk.StringVar()

options = [
    "轮挡、反光锥形标志物放置操作时间-ABC",
    "轮挡、反光锥形标志物放置操作时间-DEF",
    "单桥对接作业时间",
    "双桥对接作业时间",
    "三桥对接作业时间",
    "单客梯车对接操作时间",
    "多客梯车对接操作时间",
    "单桥撤离作业时间",
    "双桥撤离作业时间",
    "三桥撤离作业时间",
    "单客梯车撤离操作时间",
    "多客梯车撤离操作时间",
    "牵引车对接操作时间",
    "轮挡、反光锥形标志物撤离操作时间-ABC",
    "轮挡、反光锥形标志物撤离操作时间-DEF"
]

for index, option_text in enumerate(options):
    radio_button = tk.Radiobutton(
        scrollable_frame_2,
        text=option_text,
        variable=selected_option_2,
        value=option_text,
        anchor='w',
        justify=tk.LEFT,
        wraplength=300
    )
    radio_button.grid(row=index, column=0, padx=10, pady=1, sticky=tk.W, columnspan=2)

selected_option_2.set(None)
##############################################################
#########################################################3
# 创建第三个子选项卡
tab1_3 = ttk.Frame(notebook1)
notebook1.add(tab1_3, text="作业完成时间")

#可滚动区域
checkbox_frame_3 = ttk.Frame(tab1_3)
checkbox_frame_3.grid(row=3, column=0, padx=10, pady=10, columnspan=4, sticky=tk.W)

scroll_frame_3 = ttk.Frame(checkbox_frame_3, borderwidth=2, relief="solid")
scroll_frame_3.pack(side="left", fill="both", expand=True)

canvas_3 = tk.Canvas(scroll_frame_3, height=250)
scrollbar_3 = ttk.Scrollbar(scroll_frame_3, orient="vertical", command=canvas_3.yview)
scrollable_frame_3 = ttk.Frame(canvas_3)

scrollable_frame_3.bind(
    "<Configure>",
    lambda e: canvas_3.configure(scrollregion=canvas_3.bbox("all"))
)

canvas_3.create_window((0, 0), window=scrollable_frame_3, anchor="nw")
canvas_3.configure(yscrollcommand=scrollbar_3.set)

canvas_3.pack(side="left", fill="both", expand=True)
scrollbar_3.pack(side="right", fill="y")

def on_enter(event):
    # 鼠标进入事件处理函数
    canvas_3.bind_all("<MouseWheel>", on_mousewheel_3)

def on_leave(event):
    # 鼠标离开事件处理函数
    canvas_3.unbind_all("<MouseWheel>")

# 绑定鼠标进入和离开事件
scrollable_frame_3.bind("<Enter>", on_enter)
scrollable_frame_3.bind("<Leave>", on_leave)
def on_mousewheel_3(event):
    # 鼠标滚轮事件处理函数
    # Delta为正表示向上滚动，为负表示向下滚动
    delta_3 = -event.delta // 120
    canvas_3.yview_scroll(delta_3, "units")

# 绑定鼠标滚轮事件
canvas_3.bind("<MouseWheel>", on_mousewheel_3)
# 将整个scroll_frame放入checkbox_frame
scroll_frame_3.pack(side="left", fill="both", expand=True)

selected_option_3 = tk.StringVar()

options = [
    "客舱清洁完成时间",
    "污水操作完成时间",
    "清水操作完成时间",
    "餐食及机供品配供完成时间",
    "非载客航油加注完成时间",
    "载客航油加注完成时间",
    "近机位登机口开放时间-F",
    "近机位登机口开放时间-其他",
    "远机位登机口开放时间",
    "登机口关闭时间",
    "行李装载开始时间",
    "客舱门关闭完成时间",
    "货舱门关闭完成时间"
]

for index, option_text in enumerate(options):
    radio_button = tk.Radiobutton(
        scrollable_frame_3,
        text=option_text,
        variable=selected_option_3,
        value=option_text,
        anchor='w',
        justify=tk.LEFT,
        wraplength=300
    )
    radio_button.grid(row=index, column=0, padx=10, pady=1, sticky=tk.W, columnspan=2)

selected_option_3.set(None)
##############################################################
#########################################################3
# 创建第四个子选项卡
tab1_4 = ttk.Frame(notebook1)
notebook1.add(tab1_4, text="作业衔接时间")

#可滚动区域
checkbox_frame_4 = ttk.Frame(tab1_4)
checkbox_frame_4.grid(row=3, column=0, padx=10, pady=10, columnspan=4, sticky=tk.W)

scroll_frame_4 = ttk.Frame(checkbox_frame_4, borderwidth=2, relief="solid")
scroll_frame_4.pack(side="left", fill="both", expand=True)

canvas_4 = tk.Canvas(scroll_frame_4, height=250)
scrollbar_4 = ttk.Scrollbar(scroll_frame_4, orient="vertical", command=canvas_4.yview)
scrollable_frame_4 = ttk.Frame(canvas_4)

scrollable_frame_4.bind(
    "<Configure>",
    lambda e: canvas_4.configure(scrollregion=canvas_4.bbox("all"))
)

canvas_4.create_window((0, 0), window=scrollable_frame_4, anchor="nw")
canvas_4.configure(yscrollcommand=scrollbar_4.set)

canvas_4.pack(side="left", fill="both", expand=True)
scrollbar_4.pack(side="right", fill="y")

def on_enter(event):
    # 鼠标进入事件处理函数
    canvas_4.bind_all("<MouseWheel>", on_mousewheel_4)

def on_leave(event):
    # 鼠标离开事件处理函数
    canvas_4.unbind_all("<MouseWheel>")

# 绑定鼠标进入和离开事件
scrollable_frame_4.bind("<Enter>", on_enter)
scrollable_frame_4.bind("<Leave>", on_leave)
def on_mousewheel_4(event):
    # 鼠标滚轮事件处理函数
    # Delta为正表示向上滚动，为负表示向下滚动
    delta_4 = -event.delta // 120
    canvas_4.yview_scroll(delta_4, "units")

# 绑定鼠标滚轮事件
canvas_4.bind_all("<MouseWheel>", on_mousewheel_4)
# 将整个scroll_frame放入checkbox_frame
scroll_frame_4.pack(side="left", fill="both", expand=True)

selected_option_4 = tk.StringVar()

options = [
    "机务给指令与廊桥对接的衔接时间",
    "机务给指令与客梯车对接的衔接时间",
    "开货门至卸行李货邮时间-ABC",
    "开货门至卸行李货邮时间-DEF",
    "清洁作业开始时间",
    "客舱门关闭与最后一个廊桥撤离的衔接",
    "客舱门关闭与最后一辆客梯车撤离的衔接",
    "关舱门至首次RDY时间",
    "接到指令到航空器开始推离机位时间(未对接)",
    "接到指令到航空器开始推离机位时间(已对接)"
]

for index, option_text in enumerate(options):
    radio_button = tk.Radiobutton(
        scrollable_frame_4,
        text=option_text,
        variable=selected_option_4,
        value=option_text,
        anchor='w',
        justify=tk.LEFT,
        wraplength=300
    )
    radio_button.grid(row=index, column=0, padx=10, pady=1, sticky=tk.W, columnspan=2)

selected_option_4.set(None)
################################################################################################
#########################################################3
# 创建第四个子选项卡
tab1_5 = ttk.Frame(notebook1)
notebook1.add(tab1_5, text="快速过站指标")

#可滚动区域
checkbox_frame_5 = ttk.Frame(tab1_5)
checkbox_frame_5.grid(row=3, column=0, padx=10, pady=10, columnspan=4, sticky=tk.W)

scroll_frame_5 = ttk.Frame(checkbox_frame_5, borderwidth=2, relief="solid")
scroll_frame_5.pack(side="left", fill="both", expand=True)

canvas_5 = tk.Canvas(scroll_frame_5, height=250)
scrollbar_5 = ttk.Scrollbar(scroll_frame_5, orient="vertical", command=canvas_5.yview)
scrollable_frame_5 = ttk.Frame(canvas_5)

scrollable_frame_5.bind(
    "<Configure>",
    lambda e: canvas_5.configure(scrollregion=canvas_5.bbox("all"))
)

canvas_5.create_window((0, 0), window=scrollable_frame_5, anchor="nw")
canvas_5.configure(yscrollcommand=scrollbar_5.set)

canvas_5.pack(side="left", fill="both", expand=True)
scrollbar_5.pack(side="right", fill="y")

def on_enter(event):
    # 鼠标进入事件处理函数
    canvas_5.bind_all("<MouseWheel>", on_mousewheel_5)

def on_leave(event):
    # 鼠标离开事件处理函数
    canvas_5.unbind_all("<MouseWheel>")

# 绑定鼠标进入和离开事件
scrollable_frame_5.bind("<Enter>", on_enter)
scrollable_frame_5.bind("<Leave>", on_leave)
def on_mousewheel_5(event):
    # 鼠标滚轮事件处理函数
    # Delta为正表示向上滚动，为负表示向下滚动
    delta_5 = -event.delta // 120
    canvas_5.yview_scroll(delta_5, "units")

# 绑定鼠标滚轮事件
canvas_5.bind_all("<MouseWheel>", on_mousewheel_5)
# 将整个scroll_frame放入checkbox_frame
scroll_frame_5.pack(side="left", fill="both", expand=True)

selected_option_5 = tk.StringVar()

options = [
    "快速过站旅客下机-C",
    "快速过站旅客下机-E",
    "快速过站配餐-C",
    "快速过站配餐-E",
    "快速过站清洁-C",
    "快速过站清洁-E",
    "快速过站加油-C",
    "快速过站加油-E",
    "快速过站旅客登机-C",
    "快速过站旅客登机-E",
    '快速过站客舱清洁完成时间_下客结束-ABC',
    '快速过站客舱清洁完成时间_下客结束-DEF',
    '快速过站客舱清洁完成时间_上轮挡-ABC',
    '快速过站客舱清洁完成时间_上轮挡-DEF',
    '快速过站配餐完成时间_下客结束-ABC',
    '快速过站配餐完成时间_下客结束-DEF',
    '快速过站配餐完成时间_上轮挡-ABC',
    '快速过站配餐完成时间_上轮挡-DEF',
    '快速过站登机口开放时间_近机位-ABC',
    '快速过站登机口开放时间_近机位-DEF',
    '快速过站登机口开放时间_远机位-ABC',
    '快速过站登机口开放时间_远机位-DEF'
]

for index, option_text in enumerate(options):
    radio_button = tk.Radiobutton(
        scrollable_frame_5,
        text=option_text,
        variable=selected_option_5,
        value=option_text,
        anchor='w',
        justify=tk.LEFT,
        wraplength=300
    )
    radio_button.grid(row=index, column=0, padx=10, pady=1, sticky=tk.W, columnspan=2)

selected_option_5.set(None)
################################################################################################

# 创建运行程序的按钮
process_button = tk.Button(tab1, text="运行程序", command=process_file, height=1, width=15, bg="#5cb85c", fg="white")
process_button.grid(row=9, column=1, padx=10, pady=10, columnspan=2)

# 在切换选项卡时，清除掉其他选项卡上勾选的选项
def on_tab_change_1(event):
    current_tab = notebook1.index(notebook1.select())
    if current_tab != 0:
        selected_option1.set(None)
    if current_tab != 1:
        selected_option_2.set(None)
    if current_tab != 2:
        selected_option_3.set(None)
    if current_tab != 3:
        selected_option_4.set(None)
    if current_tab != 4:
        selected_option_5.set(None)

notebook1.bind("<<NotebookTabChanged>>", on_tab_change_1)

# 创建第二个选项卡
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="数据清洗")

# 列名输入框
qx_col1_label = tk.Label(tab2, text="开始节点列名：")
qx_col1_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

qx_col1_entry = tk.Entry(tab2, width=20)
qx_col1_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

qx_col2_label = tk.Label(tab2, text="结束节点列名：")
qx_col2_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

qx_col2_entry = tk.Entry(tab2, width=20)
qx_col2_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

# 阈值输入框
qx_lower_threshold_label = tk.Label(tab2, text="差值大于等于：")
qx_lower_threshold_label.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)

qx_lower_threshold_entry = tk.Entry(tab2, width=10)
qx_lower_threshold_entry.grid(row=1, column=3, padx=10, pady=10, sticky=tk.W)

qx_upper_threshold_label = tk.Label(tab2, text="差值小于等于：")
qx_upper_threshold_label.grid(row=2, column=2, padx=10, pady=10, sticky=tk.W)

qx_upper_threshold_entry = tk.Entry(tab2, width=10)
qx_upper_threshold_entry.grid(row=2, column=3, padx=10, pady=10, sticky=tk.W)

# 处理按钮
qx_process_button = tk.Button(tab2, text="检查数据", command=process_data)
qx_process_button.grid(row=3, column=1, pady=20, sticky=tk.E)

# 处理结果文本框
result_text = tk.Text(tab2, height=10, width=60)
result_text.grid(row=4, column=0, columnspan=4, padx=10, pady=10)
# 创建一个垂直滚动条
scrollbar_qx = tk.Scrollbar(tab2, orient="vertical", command=result_text.yview)
scrollbar_qx.grid(row=4, column=4, sticky="ns")
# 将文本框与滚动条关联
result_text.config(yscrollcommand=scrollbar_qx.set)

##########################################################################
# 创建第三个选项卡
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="自定义计算")

# 列名输入框
col1_label = tk.Label(tab3, text="保障环节名称：")
col1_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

col1_entry = tk.Entry(tab3, width=20)
col1_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

col2_label = tk.Label(tab3, text="开始节点列名：")
col2_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

col2_entry = tk.Entry(tab3, width=20)
col2_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)

col3_label = tk.Label(tab3, text="结束节点列名：")
col3_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

col3_entry = tk.Entry(tab3, width=20)
col3_entry.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

# 选择指标类型-下拉框
col4_entry = tk.StringVar(value="协同指标驱动类")  # 默认选择协同指标驱动类
col4_label = tk.Label(tab3, text="指标类型:")
col4_label.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)

# 使用ttk的Combobox
col4_combobox = ttk.Combobox(tab3, textvariable=col4_entry, values=["协同指标驱动类", "前后环节衔接类", "持续时间类"], state="readonly",
                             width=15)

# 设置下拉箭头的样式
style = ttk.Style()
style.configure("TCombobox", padding=5, relief="flat", borderwidth=1)

col4_combobox["style"] = "TCombobox"

col4_combobox.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)

# 阈值输入框
lower_threshold1_label = tk.Label(tab3, text="正常值下界：")
lower_threshold1_label.grid(row=2, column=2, padx=10, pady=10, sticky=tk.W)
lower_threshold1_entry = tk.Entry(tab3, width=10)
lower_threshold1_entry.grid(row=2, column=3, padx=10, pady=10, sticky=tk.W)
upper_threshold1_label = tk.Label(tab3, text="正常值上界：")
upper_threshold1_label.grid(row=3, column=2, padx=10, pady=10, sticky=tk.W)
upper_threshold1_entry = tk.Entry(tab3, width=10)
upper_threshold1_entry.grid(row=3, column=3, padx=10, pady=10, sticky=tk.W)
lower_threshold2_label = tk.Label(tab3, text="符合标准下界：")
lower_threshold2_label.grid(row=4, column=2, padx=10, pady=10, sticky=tk.W)
lower_threshold2_entry = tk.Entry(tab3, width=10)
lower_threshold2_entry.grid(row=4, column=3, padx=10, pady=10, sticky=tk.W)
upper_threshold2_label = tk.Label(tab3, text="符合标准上界：")
upper_threshold2_label.grid(row=5, column=2, padx=10, pady=10, sticky=tk.W)
upper_threshold2_entry = tk.Entry(tab3, width=10)
upper_threshold2_entry.grid(row=5, column=3, padx=10, pady=10, sticky=tk.W)

# 处理按钮
process_button = tk.Button(tab3, text="开始计算", command=process_user, height=1, width=10, bg="#5cb85c", fg="white")
process_button.grid(row=9, column=1, pady=20, sticky=tk.E)

# 创建第四个选项卡
tab4 = ttk.Frame(notebook)
notebook.add(tab4, text=" 过站航班评分 ")

##第一列
tab4_col0_label = tk.Label(tab4, text="作业")
tab4_col0_label.grid(row=1, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col01_label = tk.Label(tab4, text="时间（分钟）")
tab4_col01_label.grid(row=1, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col1_label = tk.Label(tab4, text="A拖曳飞机到达出港机位")
tab4_col1_label.grid(row=2, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col1_entry = tk.Entry(tab4, width=10)
tab4_col1_entry.grid(row=2, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col2_label = tk.Label(tab4, text="A引导车到达指定引导位置")
tab4_col2_label.grid(row=3, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col2_entry = tk.Entry(tab4, width=10)
tab4_col2_entry.grid(row=3, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col3_label = tk.Label(tab4, text="A机务到达机位")
tab4_col3_label.grid(row=4, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col3_entry = tk.Entry(tab4, width=10)
tab4_col3_entry.grid(row=4, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col4_label = tk.Label(tab4, text="A客梯车到达机位")
tab4_col4_label.grid(row=5, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col4_entry = tk.Entry(tab4, width=10)
tab4_col4_entry.grid(row=5, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col5_label = tk.Label(tab4, text="A进港首辆摆渡车到达机位")
tab4_col5_label.grid(row=6, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col5_entry = tk.Entry(tab4, width=10)
tab4_col5_entry.grid(row=6, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col6_label = tk.Label(tab4, text="A地服接机人员到位")
tab4_col6_label.grid(row=7, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col6_entry = tk.Entry(tab4, width=10)
tab4_col6_entry.grid(row=7, column=1, padx=10, pady=1, sticky=tk.W)
# tab4_col6_label = tk.Label(tab4, text="A机位类型")
# tab4_col6_label.grid(row=7, column=0, padx=10, pady=1, sticky=tk.W)
# tab4_col6_entry = tk.StringVar(value="近")
# tab4_combobox1 = ttk.Combobox(tab4, textvariable=tab4_col6_entry, values=["近", "远"], state="readonly", width=5)
# tab4_combobox1["style"] = "TCombobox"
# tab4_combobox1.grid(row=7, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col7_label = tk.Label(tab4, text="A装卸人员及装卸设备到位", wraplength=200, justify="left")
tab4_col7_label.grid(row=8, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col7_entry = tk.Entry(tab4, width=10)
tab4_col7_entry.grid(row=8, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col8_label = tk.Label(tab4, text="A清洁人员到达机位")
tab4_col8_label.grid(row=9, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col8_entry = tk.Entry(tab4, width=10)
tab4_col8_entry.grid(row=9, column=1, padx=10, pady=1, sticky=tk.W)
tab4_col9_label = tk.Label(tab4, text="A机组和乘务到达机位")
tab4_col9_label.grid(row=10, column=0, padx=10, pady=1, sticky=tk.W)
tab4_col9_entry = tk.Entry(tab4, width=10)
tab4_col9_entry.grid(row=10, column=1, padx=10, pady=1, sticky=tk.W)
tab4_cola_label = tk.Label(tab4, text="A出港首辆摆渡车到达登机口")
tab4_cola_label.grid(row=11, column=0, padx=10, pady=1, sticky=tk.W)
tab4_cola_entry = tk.Entry(tab4, width=10)
tab4_cola_entry.grid(row=11, column=1, padx=10, pady=1, sticky=tk.W)
# tab4_cola_label = tk.Label(tab4, text="B选择评分指标")
# tab4_cola_label.grid(row=11, column=0, padx=10, pady=1, sticky=tk.W)
# tab4_cola_entry = tk.StringVar(value="廊桥")
# tab4_combobox2 = ttk.Combobox(tab4, textvariable=tab4_cola_entry, values=["廊桥", "客梯车"], state="readonly", width=5)
# tab4_combobox2["style"] = "TCombobox"
# tab4_combobox2.grid(row=11, column=1, padx=10, pady=1, sticky=tk.W)
tab4_colb_label = tk.Label(tab4, text="A出港最后一辆摆渡车到达远机位", wraplength=200, justify="left")
tab4_colb_label.grid(row=12, column=0, padx=10, pady=1, sticky=tk.W)
tab4_colb_entry = tk.Entry(tab4, width=10)
tab4_colb_entry.grid(row=12, column=1, padx=10, pady=1, sticky=tk.W)
tab4_colc_label = tk.Label(tab4, text="A牵引车、机务、拖把到达机位", wraplength=200, justify="left")
tab4_colc_label.grid(row=13, column=0, padx=10, pady=1, sticky=tk.W)
tab4_colc_entry = tk.Entry(tab4, width=10)
tab4_colc_entry.grid(row=13, column=1, padx=10, pady=1, sticky=tk.W)
# tab4_colc_label = tk.Label(tab4, text="航后航班进港正常")
# tab4_colc_label.grid(row=13, column=0, padx=10, pady=1, sticky=tk.W)
# tab4_colc_entry = tk.StringVar(value="是")
# tab4_combobox2 = ttk.Combobox(tab4, textvariable=tab4_colc_entry, values=["是", "否"], state="readonly", width=5)
# tab4_combobox2["style"] = "TCombobox"
# tab4_combobox2.grid(row=13, column=1, padx=10, pady=1, sticky=tk.W)
# tab4_cold_label = tk.Label(tab4, text="进港滑行时间在12分钟内")
# tab4_cold_label.grid(row=14, column=0, padx=10, pady=1, sticky=tk.W)
# tab4_cold_entry = tk.StringVar(value="是")
# tab4_combobox2 = ttk.Combobox(tab4, textvariable=tab4_cold_entry, values=["是", "否"], state="readonly", width=5)
# tab4_combobox2["style"] = "TCombobox"
# tab4_combobox2.grid(row=14, column=1, padx=10, pady=1, sticky=tk.W)
tab4_cold_label = tk.Label(tab4, text="B登机口开放", wraplength=200, justify="left")
tab4_cold_label.grid(row=14, column=0, padx=10, pady=1, sticky=tk.W)
tab4_cold_entry = tk.Entry(tab4, width=10)
tab4_cold_entry.grid(row=14, column=1, padx=10, pady=1, sticky=tk.W)
tab4_cole_label = tk.Label(tab4, text="B行李装载开始", wraplength=140, justify="left")
tab4_cole_label.grid(row=15, column=0, padx=10, pady=1, sticky=tk.W)
tab4_cole_entry = tk.Entry(tab4, width=10)
tab4_cole_entry.grid(row=15, column=1, padx=10, pady=1, sticky=tk.W)
tab4_colf_label = tk.Label(tab4, text="B通知翻找行李", wraplength=140, justify="left")
tab4_colf_label.grid(row=16, column=0, padx=10, pady=1, sticky=tk.W)
tab4_colf_entry = tk.Entry(tab4, width=10)
tab4_colf_entry.grid(row=16, column=1, padx=10, pady=1, sticky=tk.W)
tab4_colg_label = tk.Label(tab4, text="B实挑实减行李", wraplength=140, justify="left")
tab4_colg_label.grid(row=17, column=0, padx=10, pady=1, sticky=tk.W)
tab4_colg_entry = tk.Entry(tab4, width=10)
tab4_colg_entry.grid(row=17, column=1, padx=10, pady=1, sticky=tk.W)

##第2列
def create_entry_labels(tab, entries,col):
    entry_dict = {}  # 创建一个空字典用于存储输入框对象

    for i, entry_data in enumerate(entries, start=2):
        label_text, default_value = entry_data
        label = tk.Label(tab, text=label_text, wraplength=210, justify="left")
        label.grid(row=i, column=(col*2-2), padx=10, pady=1, sticky=tk.W)
        entry = tk.Entry(tab, width=10)
        entry.grid(row=i, column=(col*2-1), padx=10, pady=1, sticky=tk.W)
        entry.insert(0, default_value)
        entry_dict[label_text] = entry  # 将输入框对象与标签文本关联起来

    return entry_dict

entries_col2 = [
    ("C轮挡、反光锥形标志物放置时间", ""),
    ("C廊桥/客梯车对接操作时间", ""),
    ("C客舱门开启操作时间", ""),
    ("C客舱门关闭操作时间", ""),
    ("C货舱门关闭操作时间", ""),
    ("C廊桥/客梯车撤离操作时间", ""),
    ("C牵引车对接操作时间", ""),
    ("C轮挡、反光锥形标志物撤离时间", ""),
    ("D申请拖曳时间", ""),
    ("D廊桥检查及准备工作完成时间", ""),
    # ("D廊桥/客梯车对接完成", ""),
    ("D清洁完成", ""),
    ("D清水完成", ""),
    ("D污水完成", ""),
    ("D配餐完成", ""),
    ("D加油完成", ""),
    ("D登机完成并关闭登机口", "")
]
tab4_col001_label = tk.Label(tab4, text="作业")
tab4_col001_label.grid(row=1, column=2, padx=10, pady=1, sticky=tk.W)
tab4_col011_label = tk.Label(tab4, text="时间（分钟）")
tab4_col011_label.grid(row=1, column=3, padx=10, pady=1, sticky=tk.W)
entry_dict_col2 = create_entry_labels(tab4, entries_col2,2)

# 通过标签文本定位对应的输入框
tab4_c2r1_entry = entry_dict_col2["C轮挡、反光锥形标志物放置时间"]
tab4_c2r2_entry = entry_dict_col2["C廊桥/客梯车对接操作时间"]
tab4_c2r3_entry = entry_dict_col2["C客舱门开启操作时间"]
tab4_c2r4_entry = entry_dict_col2["C客舱门关闭操作时间"]
tab4_c2r5_entry = entry_dict_col2["C货舱门关闭操作时间"]
tab4_c2r6_entry = entry_dict_col2["C廊桥/客梯车撤离操作时间"]
tab4_c2r7_entry = entry_dict_col2["C牵引车对接操作时间"]
tab4_c2r8_entry = entry_dict_col2["C轮挡、反光锥形标志物撤离时间"]
tab4_c2r9_entry = entry_dict_col2["D申请拖曳时间"]
tab4_c2r10_entry = entry_dict_col2["D廊桥检查及准备工作完成时间"]
tab4_c2r12_entry = entry_dict_col2["D清洁完成"]
tab4_c2r13_entry = entry_dict_col2["D清水完成"]
tab4_c2r14_entry = entry_dict_col2["D污水完成"]
tab4_c2r15_entry = entry_dict_col2["D配餐完成"]
tab4_c2r16_entry = entry_dict_col2["D加油完成"]
tab4_c3r1_entry = entry_dict_col2["D登机完成并关闭登机口"]

#第三列
entries_col3 = [
    ("D舱单上传完成", ""),
    ("D客舱门关闭", ""),
    ("D货舱门关闭", ""),
    ("D引导车引导信息通报", ""),
    ("E机务给对接指令-廊桥/客梯车对接", ""),
    ("E廊桥/客梯车对接完成-开启客舱门", ""),
    ("E开货门-卸载行李货邮", ""),
    ("E旅客下机完毕-清洁作业开始", ""),
    ("E客舱门关闭-最后一个廊桥/客梯车撤离", ""),
    ("E关舱门-首次RDY", ""),
    ("E接到指令-推离机位", ""),
    ("E引导车接到指令-到达指定位置", ""),
]
tab4_col002_label = tk.Label(tab4, text="作业")
tab4_col002_label.grid(row=1, column=4, padx=10, pady=1, sticky=tk.W)
tab4_col012_label = tk.Label(tab4, text="时间（分钟）")
tab4_col012_label.grid(row=1, column=5, padx=10, pady=1, sticky=tk.W)
entry_dict_col3 = create_entry_labels(tab4, entries_col3,3)

tab4_c3r2_entry = entry_dict_col3["D舱单上传完成"]
tab4_c3r4_entry = entry_dict_col3["D客舱门关闭"]
tab4_c3r5_entry = entry_dict_col3["D货舱门关闭"]
tab4_c3r6_entry = entry_dict_col3["D引导车引导信息通报"]
tab4_c3r7_entry = entry_dict_col3["E机务给对接指令-廊桥/客梯车对接"]
tab4_c3r8_entry = entry_dict_col3["E廊桥/客梯车对接完成-开启客舱门"]
tab4_c3r9_entry = entry_dict_col3["E开货门-卸载行李货邮"]
tab4_c3r10_entry = entry_dict_col3["E旅客下机完毕-清洁作业开始"]
tab4_c3r11_entry = entry_dict_col3["E客舱门关闭-最后一个廊桥/客梯车撤离"]
tab4_c3r12_entry = entry_dict_col3["E关舱门-首次RDY"]
tab4_c3r13_entry = entry_dict_col3["E接到指令-推离机位"]
tab4_c3r14_entry = entry_dict_col3["E引导车接到指令-到达指定位置"]

#可以设置frame
#需要加的几个额外数据：近远机位、机型、是否加餐、是否载客加油、接到推出指令时是否已对接
entries_col4 = [
    ("近/远机位", "近"),  # 影响航班使用廊桥还是客梯车
    ("机型", "C"),  # 影响航班保障的指标
    ("是否加餐", "否"),  # 影响配餐完成时间
    ("是否载客加油", "否"),  # 影响加油完成时间
    ("接到推出指令时是否已对接", "否"),  # 影响接到指令和推离机位衔接时间
    ("廊桥/客梯车数量", ""),  # 影响计算指标符合情况
]

tab4_col003_label = tk.Label(tab4, text="航班信息")
tab4_col003_label.grid(row=1, column=6, padx=10, pady=1, sticky=tk.W)
tab4_col013_label = tk.Label(tab4, text="")
tab4_col013_label.grid(row=1, column=7, padx=10, pady=1, sticky=tk.W)
entry_dict_col4 = create_entry_labels(tab4, entries_col4,4)
tab4_c4r1_entry = entry_dict_col4["近/远机位"]
tab4_c4r2_entry = entry_dict_col4["机型"]
tab4_c4r3_entry = entry_dict_col4["是否加餐"]
tab4_c4r4_entry = entry_dict_col4["是否载客加油"]
tab4_c4r5_entry = entry_dict_col4["接到推出指令时是否已对接"]
tab4_c4r6_entry = entry_dict_col4["廊桥/客梯车数量"]

# 在计算平均分的时候，出来的整体分析界面可以把这几项的符合率也附上
tab4_F1_label = tk.Label(tab4, text="过站航班起飞正常(ATOT-STD-30min)", wraplength=210, justify="left")
tab4_F1_label.grid(row=9, column=6, padx=10, pady=1, sticky=tk.W)
tab4_F1_entry = tk.Entry(tab4, width=10)
tab4_F1_entry.grid(row=9, column=7, padx=10, pady=1, sticky=tk.W)
tab4_F2_label = tk.Label(tab4, text="COBT符合性(AOBT-COBT)", wraplength=210, justify="left")
tab4_F2_label.grid(row=10, column=6, padx=10, pady=1, sticky=tk.W)
tab4_F2_entry = tk.Entry(tab4, width=10)
tab4_F2_entry.grid(row=10, column=7, padx=10, pady=1, sticky=tk.W)
tab4_F3_label = tk.Label(tab4, text="CTOT符合性(ATOT-CTOT)", wraplength=210, justify="left")
tab4_F3_label.grid(row=11, column=6, padx=10, pady=1, sticky=tk.W)
tab4_F3_entry = tk.Entry(tab4, width=10)
tab4_F3_entry.grid(row=11, column=7, padx=10, pady=1, sticky=tk.W)
tab4_F4_label = tk.Label(tab4, text="进港滑行时间(AIBT-ALDT)", wraplength=210, justify="left")
tab4_F4_label.grid(row=12, column=6, padx=10, pady=1, sticky=tk.W)
tab4_F4_entry = tk.Entry(tab4, width=10)
tab4_F4_entry.grid(row=12, column=7, padx=10, pady=1, sticky=tk.W)
tab4_F5_label = tk.Label(tab4, text="离港滑行时间(ATOT-AOBT)", wraplength=210, justify="left")
tab4_F5_label.grid(row=13, column=6, padx=10, pady=1, sticky=tk.W)
tab4_F5_entry = tk.Entry(tab4, width=10)
tab4_F5_entry.grid(row=13, column=7, padx=10, pady=1, sticky=tk.W)
tab4_F6_label = tk.Label(tab4, text="放行延误时间", wraplength=210, justify="left")
tab4_F6_label.grid(row=14, column=6, padx=10, pady=1, sticky=tk.W)
tab4_F6_entry = tk.Entry(tab4, width=10)
tab4_F6_entry.grid(row=14, column=7, padx=10, pady=1, sticky=tk.W)
tab4_F7_label = tk.Label(tab4, text="是否进港延误", wraplength=210, justify="left")
tab4_F7_label.grid(row=15, column=6, padx=10, pady=1, sticky=tk.W)
tab4_F7_entry = tk.Entry(tab4, width=10)
tab4_F7_entry.grid(row=15, column=7, padx=10, pady=1, sticky=tk.W)

tab4_col1b_button1 = tk.Button(tab4, text="读取数据", command=readcsv)
tab4_col1b_button1.grid(row=19, column=7, padx=10, pady=1, sticky=tk.W)
tab4_col1b_label = tk.Label(tab4, text="目标\n航班序号", wraplength=140)
tab4_col1b_label.grid(row=19, column=8, padx=10, pady=1, sticky=tk.W)
tab4_col1b_entry = tk.Entry(tab4, width=10)
tab4_col1b_entry.grid(row=19, column=9, padx=10, pady=1, sticky=tk.W)
tab4_col1b_entry.insert(0, 1)
tab4_col1c_button2 = tk.Button(tab4, text="计算评分", command=cal_score, width=18, bg="#5cb85c", fg="white")
tab4_col1c_button2.grid(row=20, column=7, padx=10, pady=1, sticky=tk.W, columnspan=2)
tab4_col1c_entry = tk.Entry(tab4, width=10)
tab4_col1c_entry.grid(row=20, column=9, padx=10, pady=1, sticky=tk.W)

tab4_col1d_button2 = tk.Button(tab4, text="计算所有航班平均分", command=browse_input_path, width=18, bg="#5cb85c", fg="white")
tab4_col1d_button2.grid(row=21, column=7, padx=10, pady=40, sticky=tk.W, columnspan=2)
tab4_col1d_entry = tk.Entry(tab4, width=10)
tab4_col1d_entry.grid(row=21, column=9, padx=10, pady=40, sticky=tk.W)

# 创建第五个选项卡
tab5 = ttk.Frame(notebook)
notebook.add(tab5, text="版本信息")

# 添加版本信息和功能说明文档
function_text = tk.Text(tab5, wrap="word", height=10, width=65)
function_text.insert("1.0", "版本Ver1.00\n")
function_text.tag_configure("bold", font=("Helvetica", 10, "bold"))
function_text.tag_add("bold", "1.0", "1.12")  # 将第一行文字应用 bold 样式
function_text.insert("2.0", "1.加入了单输入参数的指标的计算\n2.可实现功能具体请参考“程序说明文档\n\n")

function_text.insert("5.0", "版本Ver1.10\n")
function_text.tag_configure("bold", font=("Helvetica", 10, "bold"))
function_text.tag_add("bold", "5.0", "5.12")  # 将第一行文字应用 bold 样式
function_text.insert("6.0", "1.实现了所有过站指标的统计\n"
                            "2.将导入功能修改为统计结果可视化\n"
                            "3.修改了导入文件和导出文件的位置，目前“导出文件”功能暂时没有用处，仅限展示\n"
                            "4.调整了选项卡文本\n\n")
function_text.pack(pady=10)

# 运行UI循环
root.mainloop()
