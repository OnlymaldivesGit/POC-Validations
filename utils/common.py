"""
utils/common.py — Shared UI helper functions.

Moved from Commonfunction.py without any logic changes.
"""

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode


def show_aggrid(df: pd.DataFrame, grid_key: str) -> None:
    """
    Rule: N/A
    Purpose: Render a pandas DataFrame as a fully-featured AgGrid table with
             auto-sizing columns, pagination (if > 10 rows), filtering,
             sorting, grouping, and multi-select checkboxes.

    Args:
        df:       The DataFrame to display. Any shape; all columns are included.
        grid_key: A unique Streamlit widget key string to avoid state collisions
                  when multiple grids are rendered on the same page.

    Returns:
        None (renders directly into the Streamlit page).

    Known issues:
        None
    """
    gb = GridOptionsBuilder.from_dataframe(df)

    for col in df.columns:
        gb.configure_column(col, autoWidth=True)
    gb.configure_default_column(
        filter=True, sortable=True, groupable=True,
        value=True, enableRowGroup=True, aggFunc="sum",
    )
    if len(df) > 10:
        gb.configure_pagination(enabled=True, paginationPageSize=10)
    else:
        gb.configure_pagination(enabled=False)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_side_bar(filters_panel=True)
    gb.configure_grid_options(rowGroupPanelShow="always")

    grid_options = gb.build()

    auto_size_js = JsCode("""
    function onFirstDataRendered(params) {
        var allColumnIds = [];
        params.columnApi.getAllColumns().forEach(function(column) {
            allColumnIds.push(column.getId());
        });
        params.columnApi.autoSizeColumns(allColumnIds);
    }
    """)
    grid_options["onFirstDataRendered"] = auto_size_js

    grid_height = min(400, 40 + len(df) * 35)

    AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.NO_UPDATE,
        height=grid_height,
        width="100%",
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=False,
        key=grid_key,
    )
