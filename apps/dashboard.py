import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium", app_title="LSB Bestandskonferenz")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    import numpy as np
    import urllib.request
    return alt, mo, np, pd, urllib


@app.cell
def _(mo, pd):
    def _():
        files = [
            "2017-kummulativ.csv",
            "2018-kummulativ.csv",
            "2019-kummulativ.csv",
            "2020-kummulativ.csv",
            "2021-kummulativ.csv",
            "2022-kummulativ.csv",
            "2023-kummulativ.csv",
            "2024-kummulativ.csv",
        ]

        for file in files:
            # with urllib.request.urlopen(
            with open(
                mo.notebook_location() / "public" / file,
                mode="r",
                encoding="utf-8",
            ) as f:
                df = pd.read_csv(
                    f,
                    parse_dates=["Zeitraum"],
                )

            # Calculate absolute values per library
            cols = ["Entleihungen", "Besucher", "aktivierte Ausweise"]
            df[cols] = df.groupby("Bibliothek")[cols].diff().fillna(df[cols])

            # Format output and save
            df["Zeitraum"] = df["Zeitraum"].dt.strftime("%Y-%m")
            df.sort_values(["Zeitraum", "Bibliothek"]).to_csv(
                f"{file[:4]}-absolut.csv", index=False, encoding="utf-8"
            )
    return


@app.cell
def _(pd):
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
    return df, files


@app.cell(hide_code=True)
def _(df, mo):
    bibliotheken = [
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
    ]

    online_dienste = [
        "Onleihe",
        "Overdrive",
        "Website",
        "Online-Katalog",
        "Munzinger",
        "Linkedin Learn",
        "filmfriend",
        "Code it!",
        "Pressreader",
        "TigerBooks",
        "Social Media",
        "Naxos",
        "nkoda",
        "Genios",
        "Brockhaus",
        "Medici.tv",
        "linguaTV",
        "scoyo",
        "Tilasto",
    ]

    dimension = mo.ui.dropdown(
        options=[
            "Besucher",
            "Entleihungen",
        ],
        label="Auswertungsdimension",
        value="Besucher",
    )
    bibliotheks_auswahl = mo.ui.multiselect(
        options=bibliotheken,
        label="Bibliotheken auswählen",
        value=bibliotheken,
    )
    online_auswahl = mo.ui.multiselect(
        options=online_dienste,
        label="Online-Dienste auswählen",
        value=online_dienste,
    )
    trendlinie = mo.ui.checkbox(label="Trendlinie anzeigen", value=True)
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
            "jährlich": "YE",
        },
        value="monatlich",
    )

    z_scores = mo.ui.checkbox(label="Standardisierte Werte anzeigen", value=False)

    mo.vstack(
        [
            mo.hstack(
                [dimension, bibliotheks_auswahl, online_auswahl],
                justify="space-between",
            ),
            mo.vstack([zeitfilter, auflösung], justify="start"),
            mo.hstack([trendlinie, z_scores], justify="start"),
            mo.md(
                "Standardisierte Werte bedeutet, dass im Diagramm nicht die absoluten Werte, sondern die Abweichungen vom Durchschnitt angegeben werden. Dadurch lässt sich die Performance von Bibliotheken und Online-Diensetn. Z-Score über 0 bedeutet: überdurchschnittliches Wachstum, 0 = durchschnittliches Wachstum, unter 0 = Wachstum unter dem Durchschnitt (Rückgang)"
            ),
        ]
    )
    return (
        auflösung,
        bibliotheken,
        bibliotheks_auswahl,
        dimension,
        online_auswahl,
        online_dienste,
        trendlinie,
        z_scores,
        zeitfilter,
    )


@app.cell
def _(
    alt,
    auflösung,
    bibliotheks_auswahl,
    df,
    dimension,
    online_auswahl,
    pd,
    trendlinie,
    z_scores,
    zeitfilter,
):
    # Filter data for libraries and online services
    library_data = df[
        (df.index >= zeitfilter.value[0].strftime("%Y-%m-%d"))
        & (df.index <= zeitfilter.value[1].strftime("%Y-%m-%d"))
        & df["Bibliothek"].isin(bibliotheks_auswahl.value)
    ]
    online_data = df[
        (df.index >= zeitfilter.value[0].strftime("%Y-%m-%d"))
        & (df.index <= zeitfilter.value[1].strftime("%Y-%m-%d"))
        & df["Bibliothek"].isin(online_auswahl.value)
    ]

    # Aggregate loan counts by month for libraries and online services
    library_loans = (
        library_data.groupby(pd.Grouper(freq=auflösung.value))[dimension.value]
        .sum()
        .reset_index()
    )
    online_loans = (
        online_data.groupby(pd.Grouper(freq=auflösung.value))[dimension.value]
        .sum()
        .reset_index()
    )

    library_loans.rename(columns={dimension.value: "Bibliotheken"}, inplace=True)
    online_loans.rename(columns={dimension.value: "Online-Dienste"}, inplace=True)

    # Merge the two datasets for visualization
    merged_loans = pd.merge(
        library_loans, online_loans, on="Zeitraum", how="outer"
    )

    # Prepare data for Altair visualization
    merged_loans_melted = merged_loans.melt(
        id_vars="Zeitraum", var_name="Type", value_name=dimension.value
    )

    # Create the line plot
    chart = (
        alt.Chart(merged_loans_melted)
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
            y=alt.Y(f"{dimension.value}:Q", title=f"{dimension.value}"),
            color=alt.Color("Type:N", title=""),
            tooltip=["Zeitraum", "Type", dimension.value],
        )
    )

    # z-score chart
    z_score_chart = (
        alt.Chart(merged_loans_melted)
        .transform_window(
            mean_value=f"mean({dimension.value})",
            stdev_value=f"stdev({dimension.value})",
            frame=[None, None],
            groupby=["Type"],
        )
        .transform_calculate(
            z_score=(alt.datum[dimension.value] - alt.datum.mean_value)
            / alt.datum.stdev_value
        )
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Zeitraum:T",
                axis=alt.Axis(tickCount="year", grid=True, gridColor="lightgray"),
            ),
            y=alt.Y("z_score:Q", title="Z-Score"),
            color=alt.Color("Type:N", title=""),
            tooltip=[
                "Zeitraum:T",
                alt.Tooltip("z_score:Q", title="Z-Score", format=".2f"),
                alt.Tooltip(f"{dimension.value}:Q", title=dimension.value),
            ],
        )
    )

    z_score_loess = (
        z_score_chart.transform_loess(
            on="Zeitraum",
            loess="z_score",
            groupby=["Type"],
            bandwidth=0.3,  # Adjust bandwidth for smoothing (default is 0.3)
        )
        .mark_line(strokeDash=[5, 5])
        .encode(
            x="Zeitraum:T",
            y="z_score:Q",
            color=alt.Color(
                "Type:N", title=""
            ),  # Use same color as line chart but no legend
        )
    )

    loesslines = (
        alt.Chart(merged_loans_melted)
        .transform_loess("Zeitraum", dimension.value, groupby=["Type"])
        .mark_line(color="green", strokeDash=[5, 2])
    ).encode(x="Zeitraum:T", y=f"{dimension.value}:Q", color="Type:N")

    if z_scores.value:
        if trendlinie.value:
            final_chart = z_score_loess + z_score_chart
        else:
            final_chart = z_score_chart
    else:
        if trendlinie.value:
            final_chart = chart + loesslines
        else:
            final_chart = chart

    final_chart.properties(
        title=f"{dimension.value} für Bibliotheken und Online-Dienste",
        width=850,
    )
    return (
        chart,
        final_chart,
        library_data,
        library_loans,
        loesslines,
        merged_loans,
        merged_loans_melted,
        online_data,
        online_loans,
        z_score_chart,
        z_score_loess,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
        zu stellende Fragen:

        - welche Online-Dienste sollen nicht mitgerechnet werden (Website, Katalog, Social Media)
        - welcher Dienst ist der Treiber bei den Entleihungen?
        - Darstellung des Verlaufs der Standardabweichungen: https://altair-viz.github.io/user_guide/transform/window.html
        """
    )
    return


@app.cell
def _(df):
    df
    return


if __name__ == "__main__":
    app.run()
