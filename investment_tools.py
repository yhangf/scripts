import requests as rq
import pandas as pd

def investment_income_calculator(fcode, round_, sdate, edate,
                                 dtr, p, je, stype, needfirst):
    """基金定投收益计算器
    @param fcode: 基金代码
    type fcode: str
    @param round_: 定投周期
    type round_: int, 每几个月定投一次, -7代表按周定投
    @param sdate: 定投起始日期
    type sdate: str, 形式为年月日XXXX-XX-XX
    @param edate: 定投结束日期
    type edate: str, 形式为年月日XXXX-XX-XX
    @param dtr: 定投日
    type dtr: int
    @param p: 申购费率
    type p: float, p%
    @param je: 每期定投金额
    type je: float
    @param stype: 分红类型
    type stype: int, 1代表红利再定投, 2代表现金分红
    @param needfirst: 开始日期是否为首次扣款日
    type needfirst: int, 1代表是首次扣款日期, 2反之
    """
    agent_part_1 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    agent_part_2 = "(KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    headers = {"Host": "fund.eastmoney.com",
               "Connection": "keep-alive",
               "User-Agent": agent_part_1 + agent_part_2,
               "Referer": "http://data.eastmoney.com/"}

    url_1 = "http://fund.eastmoney.com/data/FundInvestCaculator_AIPDatas.aspx?"
    url_2 = f"fcode={fcode}&sdate={sdate}&edate={edate}&shdate=&round={round_}"
    url_3 = f"&dtr={dtr}&p={p}&je={je}&stype={stype}&needfirst={needfirst}&jsoncallback=FundDTSY.result"
    url = url_1 + url_2 + url_3
    origin_data = rq.get(url, headers=headers).content.decode("utf-8")
    data = origin_data.split()[0].split(":")[1][1:].split("|")[:-1]
    return data
  
def portfolio_income_calculator(total_amount, *, code_list, ratio_list,
                                round_, sdate, edate, dtr, p, stype, needfirst):
    """基金组合定投收益计算器
    @param total_amount: 每期定投金额
    type total_amount: float
    @param code_list: 基金组合代码
    type code_list: list[str]
    @param ratio_list: 对应基金投资比例
    type ratio_list: list[float] and sum(ratio_list) == 1
    @param round_: 定投周期
    type round_: int, 每几个月定投一次, -7代表按周定投
    @param sdate: 定投起始日期
    type sdate: str, 形式为年月日XXXX-XX-XX
    @param edate: 定投结束日期
    type edate: str, 形式为年月日XXXX-XX-XX
    @param dtr: 定投日
    type dtr: int
    @param p: 申购费率
    type p: float, p%
    @param stype: 分红类型
    type stype: int, 1代表红利再定投, 2代表现金分红
    @param needfirst: 开始日是否为首次扣款日
    type needfirst: int, 1代表是首次扣款日, 2反之
    """
    if sum(ratio_list) > 1:
        raise("ratio error!")
    founds_income_list, total_principal, total_assets = [], 0, 0
    amount_allocation_list = [total_amount * ratio for ratio in ratio_list]
    for code, amount in zip(code_list, amount_allocation_list):
        founds_income_info = investment_income_calculator(code, round_, sdate, edate,
                                                          dtr, p, amount, stype, needfirst)
        founds_income_list.append(founds_income_info)
        total_principal += float(founds_income_info[3].replace(",", ""))
        total_assets += float(founds_income_info[-2].replace(",", ""))
    rate_of_return = (total_assets - total_principal) / total_principal
    return founds_income_list, total_principal, rate_of_return
  
def prety_print(founds_income_list, total_principal, rate_of_return):
    founds_income_list.append([""] * 2 +
                              ["投资组合投入总金额为", f"{total_principal:.2f}"] + 
                              ["", "投资组合总收益率为", f"{rate_of_return:.2%}"])
    df = pd.DataFrame(founds_income_list, columns=["基金代码", "基金全称", "定投总期数",
                                                   "投入总本金(元)", "分红方式", "期末总资产(元)", "定投收益率"])
    d = dict(selector="th", props=[('text-align', 'center')])
    table = (df.style.set_properties(**{'text-align': 'center'})
             .set_table_styles([d])
             .hide_index())
    return table


"""使用
return_data = portfolio_income_calculator(total_amount=2000, 
                                          code_list=["510300", "512260", "515650",
                                                     "513050", "512170"],
                                          ratio_list=[0.25, 0.2, 0.2, 0.2, 0.15],
                                          round_=1,
                                          sdate="2018-01-01", 
                                          edate="2021-04-01", 
                                          dtr=5, 
                                          p=0.01, 
                                          stype=1,
                                          needfirst=2)
founds_income_list, total_principal, rate_of_return = return_data
prety_print(founds_income_list, total_principal, rate_of_return)
"""
