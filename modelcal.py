import pandas as pd
from datetime import datetime
import warnings
from tkinter import messagebox
warnings.filterwarnings("ignore", category=FutureWarning)

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
                    if wczlow <= a <= wczup:
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
            if wczlow <= a <= wczup:
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
        if zczlow <= a <= zczup:
            Y.append(a)
        if wczlow <= a <= wczup:
            D.append(a)
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
        if wczlow <= a <= wczup:
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
        if wczlow <= a <= wczup:
            D.append(a)
    total(Y, standard, zczup, name, T, 0)
    jf(Y, 1, 0)
    perc(D, 1, 0)

# 特殊计算模块——推离机位
def cal_tc(name,dataf,mode,start,end):
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
        if wczlow <= a <= wczup:
            D.append(a)
    total(Y, standard, zczup, name, T, 0)
    jf(Y, 1, 0)
    perc(D, 1, 0)