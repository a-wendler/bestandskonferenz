import marimo

__generated_with = "0.10.17"
app = marimo.App(width="medium", app_title="LSB Bestandskonferenz")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    import numpy as np
    from pathlib import Path
    return Path, alt, mo, np, pd


@app.cell
def _(Path, pd):
    def _():
        files_names = [
            "2017-kummulativ.csv",
            "2018-kummulativ.csv",
            "2019-kummulativ.csv",
            "2020-kummulativ.csv",
            "2021-kummulativ.csv",
            "2022-kummulativ.csv",
            "2023-kummulativ.csv",
            "2024-kummulativ.csv",
        ]
        files = [Path("./public") / file for file in files_names]
        for file in files:
            df = pd.read_csv(file, parse_dates=["Zeitraum"])

            # Calculate absolute values per library
            cols = ["Entleihungen", "Besucher", "aktivierte Ausweise"]
            df[cols] = df.groupby("Bibliothek")[cols].diff().fillna(df[cols])

            # Format output and save
            df["Zeitraum"] = df["Zeitraum"].dt.strftime("%Y-%m")
            df.sort_values(["Zeitraum", "Bibliothek"]).to_csv(
                f"{file.name[:4]}-absolut.csv", index=False
            )


    _()
    return


@app.cell
def _(np, pd):
    files = [
        "2017-absolut.csv",
        "2018-absolut.csv",
        "2019-absolut.csv",
        "2020-absolut.csv",
        "2021-absolut.csv",
        "2022-absolut.csv",
        "2023-absolut.csv",
        "2024-absolut.csv",
    ]
    df = pd.concat(
        [
            pd.read_csv(
                file,
                dtype={
                    "Besucher": "Int64",
                    "Entleihungen": "Int64",
                    "aktivierte Ausweise": "Int64",
                },
                parse_dates=["Zeitraum"],
                index_col="Zeitraum",
            )
            for file in files
        ]
    )
    df["Entleihungen pro Besuch"] = df["Entleihungen"] / df["Besucher"]
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    # df
    return df, files


@app.cell(hide_code=True)
def _(df, mo):
    bibliotheksliste = [
        "Böhlitz-Ehrenberg",
        "Fahrbibliothek",
        "Gohlis",
        "Grünau-Mitte",
        "Grünau-Nord",
        "Grünau-Süd",
        "Holzhausen",
        "Lützschena-Stahmeln",
        "Mockau",
        "Paunsdorf",
        "Plagwitz",
        "Reudnitz",
        "Schönefeld",
        "Stadtbibliothek",
        "Südvorstadt",
        "Volkmarsdorf",
        "Wiederitzsch",
        "Buchsommer",
        "Onleihe",
        "Overdrive",
        "weitere Online-Dienste",
    ]

    dimension = mo.ui.dropdown(
        options=[
            "Besucher",
            "Entleihungen",
            "Entleihungen pro Besuch",
        ],
        label="Auswertungsdimension",
        value="Besucher",
    )
    bibliotheken = mo.ui.multiselect(
        options=bibliotheksliste,
        label="Bibliotheken auswählen",
        value=bibliotheksliste,
    )
    trendlinie = mo.ui.checkbox(label="Trendlinien anzeigen", value=True)
    zeitfilter = mo.ui.date_range(
        value=(
            (
                df.index.min().strftime("%Y-%m-%d"),
                df.index.max().strftime("%Y-%m-%d"),
            )
        )
    )
    auflösung = mo.ui.dropdown(
        options={
            "monatlich": "ME",
            "quartalsweise": "3ME",
            "halbjährlich": "6ME",
            "jährlich": "Y",
        },
        value="monatlich",
    )

    mo.vstack(
        [
            mo.hstack(
                [dimension, bibliotheken, trendlinie], justify="space-between"
            ),
            mo.vstack([zeitfilter, auflösung], justify="start"),
        ]
    )
    return (
        auflösung,
        bibliotheken,
        bibliotheksliste,
        dimension,
        trendlinie,
        zeitfilter,
    )


@app.cell
def _(
    alt,
    auflösung,
    bibliotheken,
    df,
    dimension,
    pd,
    trendlinie,
    zeitfilter,
):
    df_filtered = df[
        (df.index >= zeitfilter.value[0].strftime("%Y-%m-%d"))
        & (df.index <= zeitfilter.value[1].strftime("%Y-%m-%d"))
        & df["Bibliothek"].isin(bibliotheken.value)
    ]

    # df_filtered = df[df['Bibliothek'].isin(bibliotheken.value)]  # Filter rows

    # Group filtered data
    if dimension.value == "Entleihungen pro Besuch":
        df_grouped = (
            df_filtered.groupby(pd.Grouper(freq=auflösung.value))[dimension.value]
            .mean()
            .reset_index()
        )
    else:
        df_grouped = (
            df_filtered.groupby(pd.Grouper(freq=auflösung.value))[dimension.value]
            .sum()
            .reset_index()
        )

    # Create plot with filtered data
    base_chart = (
        alt.Chart(df_grouped)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Zeitraum:T",
                axis=alt.Axis(
                    tickCount="year",  # Ensure ticks are placed yearly
                    grid=True,  # Enable gridlines
                    gridColor="lightgray",  # Set gridline color (optional)
                    gridWidth=2,  # Set gridline thickness
                ),
            ),
            y=f"{dimension.value}:Q",
            tooltip=["Zeitraum", dimension.value],
        )
        .properties(
            title=f"{dimension.value} ausgewählte Bibliotheken",
            width=940,
            height=400,
        )
    )

    linear_trend = base_chart.transform_regression(
        "Zeitraum", dimension.value, method="pow"
    ).mark_line(color="firebrick", strokeWidth=2)

    # Add LOESS smoothing (non-parametric)
    loess_trend = base_chart.transform_loess(
        "Zeitraum", dimension.value
    ).mark_line(color="green", strokeDash=[5, 2])

    # Combine all layers
    final_chart = base_chart

    if trendlinie.value:
        final_chart = base_chart + linear_trend + loess_trend

    final_chart
    return (
        base_chart,
        df_filtered,
        df_grouped,
        final_chart,
        linear_trend,
        loess_trend,
    )


if __name__ == "__main__":
    app.run()
