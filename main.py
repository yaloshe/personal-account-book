# -*- coding: utf-8 -*-
"""个人记账小程序主程序（Streamlit）。

运行方式：
    pip install -r requirements.txt
    streamlit run main.py
"""

from datetime import datetime

import pandas as pd
import streamlit as st

import storage
from deepseek_client import analyze_monthly_summary

INCOME_CATEGORIES = ["工资", "奖学金", "兼职", "其他"]
EXPENSE_CATEGORIES = ["餐饮", "交通", "购物", "居住", "娱乐", "学习", "其他"]

st.set_page_config(page_title="个人记账小程序", layout="wide")
st.title("个人记账小程序")


# ---------- 侧边栏：新增账目 ----------
def render_add_form():
    with st.sidebar:
        st.header("新增账目")
        with st.form("add_form", clear_on_submit=True):
            date = st.date_input("日期", value=datetime.now().date())
            record_type = st.radio("类型", ["支出", "收入"])
            categories = EXPENSE_CATEGORIES if record_type == "支出" else INCOME_CATEGORIES
            category = st.selectbox("分类", categories)
            amount_text = st.text_input("金额（元）", placeholder="请输入大于 0 的数字")
            note = st.text_input("备注（可选）", placeholder="例如：午餐、地铁")
            submitted = st.form_submit_button("保存账目")

        if submitted:
            # 表单校验：金额不能为空、必须是数字、必须大于 0
            error = None
            amount = None
            if amount_text.strip() == "":
                error = "金额不能为空。"
            else:
                try:
                    amount = float(amount_text)
                    if amount <= 0:
                        error = "金额必须大于 0。"
                except ValueError:
                    error = "金额必须是数字。"

            if error:
                st.error(error)
                return

            record = {
                "date": date.strftime("%Y-%m-%d"),
                "type": record_type,
                "category": category,
                "amount": round(amount, 2),
                "note": note.strip(),
            }
            storage.add_record(record)
            st.success("账目已保存。")


# ---------- 主区域：筛选、列表、统计 ----------
def render_main():
    records = storage.load_records()

    # 月份选项：记录中出现过的月份 + 当前月份
    months = sorted({r["date"][:7] for r in records}, reverse=True)
    current_month = datetime.now().strftime("%Y-%m")
    if current_month not in months:
        months.insert(0, current_month)

    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("选择月份", months)
    with col2:
        selected_type = st.radio("类型筛选", ["全部", "支出", "收入"], horizontal=True)

    # 按条件过滤
    filtered = [r for r in records if r["date"][:7] == selected_month]
    if selected_type != "全部":
        filtered = [r for r in filtered if r["type"] == selected_type]

    # 月度统计（按选中月份，不受类型筛选影响，保证收支汇总完整）
    month_records = [r for r in records if r["date"][:7] == selected_month]
    total_income = sum(r["amount"] for r in month_records if r["type"] == "收入")
    total_expense = sum(r["amount"] for r in month_records if r["type"] == "支出")

    c1, c2, c3 = st.columns(3)
    c1.metric("总收入（元）", f"{total_income:.2f}")
    c2.metric("总支出（元）", f"{total_expense:.2f}")
    c3.metric("结余（元）", f"{total_income - total_expense:.2f}")

    st.subheader("账目明细")
    if filtered:
        df = pd.DataFrame(filtered)
        df = df[["date", "type", "category", "amount", "note", "id"]]
        df.columns = ["日期", "类型", "分类", "金额（元）", "备注", "编号"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 删除选中的账目
        with st.expander("删除账目"):
            ids = [r["id"] for r in filtered]
            target_id = st.selectbox("选择要删除的账目编号", ids)
            if st.button("确认删除"):
                storage.delete_record(target_id)
                st.success("已删除。")
                st.rerun()
    else:
        st.info("当前条件下暂无账目记录。")

    # ---------- AI 消费分析 ----------
    st.subheader("AI 消费分析（DeepSeek）")
    if st.button("生成本月消费分析"):
        expense_by_category = {}
        for r in month_records:
            if r["type"] == "支出":
                expense_by_category[r["category"]] = (
                    expense_by_category.get(r["category"], 0) + r["amount"]
                )
        top_categories = sorted(
            expense_by_category.items(), key=lambda x: x[1], reverse=True
        )[:5]
        answer, status = analyze_monthly_summary(
            selected_month, total_income, total_expense, top_categories
        )
        if answer:
            st.write(answer)
        st.caption(status)


if __name__ == "__main__":
    render_add_form()
    render_main()
