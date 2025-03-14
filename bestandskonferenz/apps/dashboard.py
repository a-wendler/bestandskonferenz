import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium", app_title="LSB Bestandskonferenz")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    import numpy as np
    from dateutil import relativedelta
    return alt, mo, np, pd, relativedelta


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
def _(mo, pd):
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

    try:
        df = pd.concat(
            [
                pd.read_csv(
                    mo.notebook_location() / "public" / file,
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

    except:
        df = pd.concat(
            [
                pd.read_csv(
                    f"https://raw.githubusercontent.com/a-wendler/bestandskonferenz/refs/heads/main/bestandskonferenz/apps/public/{file}",
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


@app.cell
def _(mo):
    mo.md("""# Entwicklung allgemeiner Leistungszahlen""")
    return


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
def _(mo, pd):
    jahre = ["2023", "2024"]

    try:
        buchdaten = pd.concat(
            [
                pd.read_csv(
                    mo.notebook_location() / "public" / f"buchdaten_{jahr}.csv",
                    low_memory=False,
                )
                for jahr in jahre
            ]
        )

        bestelldaten = pd.concat(
            [
                pd.read_csv(
                    mo.notebook_location() / "public" / f"bestelldaten_{jahr}.csv",
                    sep=";",
                    encoding="latin_1",
                    decimal=",",
                    thousands=".",
                    low_memory=False,
                )
                for jahr in jahre
            ]
        )

    except:
        buchdaten = pd.concat(
            [
                pd.read_csv(
                    f"https://raw.githubusercontent.com/a-wendler/bestandskonferenz/refs/heads/main/bestandskonferenz/apps/public/buchdaten_{jahr}.csv",
                    low_memory=False,
                )
                for jahr in jahre
            ]
        )

        bestelldaten = pd.concat(
            [
                pd.read_csv(
                    f"https://raw.githubusercontent.com/a-wendler/bestandskonferenz/refs/heads/main/bestandskonferenz/apps/public/bestelldaten_{jahr}.csv",
                    sep=";",
                    encoding="latin_1",
                    decimal=",",
                    thousands=".",
                    low_memory=False,
                )
                for jahr in jahre
            ]
        )

    buchdaten["exemplare"] = buchdaten.groupby("katkey")["katkey"].transform(
        "count"
    )
    bestelldaten["Bestellpreis"] = pd.to_numeric(
        bestelldaten["Bestellpreis"], errors="ignore"
    )
    buchdaten["2023_2024"] = buchdaten["2023"] + buchdaten["2024"]
    buchdaten_grouped = buchdaten.groupby("katkey", as_index=False).agg(
        {
            "Geistiger Schöpfer": "first",
            "Schlagwort": "first",
            "Signatur": "first",
            "2. Signatur": "first",
            "Gesamt": "sum",
            "2023_2024": "sum",
            "Titel": "first",
            "datumaufn": "first",
            "Mediennummer": "first",
            "Verlag": "first",
            "Erscheinungsjahr": "first",
            "Systematik": "first",
            "exemplare": "first",
        }
    )


    bestelldaten_grouped = bestelldaten.groupby("katkey", as_index=False).agg(
        {"EXEMPLARANZ": "sum", "Bestellpreis": "sum"}
    )

    gesamtdaten = pd.merge(
        buchdaten_grouped, bestelldaten_grouped, on="katkey", how="left"
    )
    gesamtdaten = gesamtdaten[gesamtdaten["katkey"] != 1952225]
    gesamtdaten = gesamtdaten[gesamtdaten["Systematik"] != 200]
    gesamtdaten.dropna(subset=["Bestellpreis"], inplace=True)
    return (
        bestelldaten,
        bestelldaten_grouped,
        buchdaten,
        buchdaten_grouped,
        gesamtdaten,
        jahre,
    )


@app.cell
def _(gesamtdaten):
    umsatz_systematik = gesamtdaten.groupby("Systematik").agg(
        {
            "exemplare": "sum",
            "Gesamt": "sum",
            "2023_2024": "sum",
            "Bestellpreis": "sum",
        }
    )
    umsatz_systematik["Umschlag"] = (
        umsatz_systematik["2023_2024"] / umsatz_systematik["exemplare"]
    )
    umsatz_systematik["Preis pro Entleihung"] = (
        umsatz_systematik["Bestellpreis"] / umsatz_systematik["2023_2024"]
    )
    return (umsatz_systematik,)


@app.cell
def _(mo):
    mo.md(r"""# Budget & Leistung physischer Bestand""")
    return


@app.cell
def _(mo):
    vergleichswert = mo.ui.dropdown(
        {
            "Umschlag": "Umschlag",
            "Gesamtentleihungen": "Gesamt",
            "Entleihungen 2023/2024 ": "2023_2024",
            "Preis pro Entleihung": "Preis pro Entleihung",
            "Exemplare im Bestand": "exemplare",
        },
        value="Umschlag",
    )
    vergleichswert
    return (vergleichswert,)


@app.cell
def _(alt, pd, umsatz_systematik, vergleichswert):
    # Get top 10 by Bestellpreis
    top_10 = umsatz_systematik.sort_values("Bestellpreis", ascending=False).head(
        10
    )
    top_10_reset = top_10.reset_index()

    # Create a new DataFrame for visualization
    chart_data = pd.melt(
        top_10_reset,
        id_vars=["Systematik"],
        value_vars=["Bestellpreis", vergleichswert.value],
        var_name="Metric",
        value_name="Value",
    )

    # Calculate max values for each metric to set appropriate domains
    bestellpreis_max = top_10_reset["Bestellpreis"].max()
    umschlag_max = top_10_reset[vergleichswert.value].max()

    # Create a list of Systematik values sorted by Bestellpreis
    sort_order = top_10_reset["Systematik"].tolist()

    # Create separate charts for each metric with appropriate domains
    bestellpreis_chart = (
        alt.Chart(chart_data.query("Metric == 'Bestellpreis'"))
        .mark_bar()
        .encode(
            x=alt.X(
                "Value:Q",
                title="Budget",
                scale=alt.Scale(
                    domain=[0, bestellpreis_max], nice=False, reverse=True
                ),
                axis=alt.Axis(format="~s"),
            ),
            y=alt.Y("Systematik:N", title="Systematik", sort=sort_order).axis(
                None
            ),
            color=alt.value("#1f77b4"),
            tooltip=[alt.Tooltip("Value", title="Budget €", format=".2r")],
        )
    )

    umschlag_chart = (
        alt.Chart(chart_data.query(f"Metric == '{vergleichswert.value}'"))
        .mark_bar()
        .encode(
            x=alt.X(
                "Value:Q",
                title=vergleichswert.selected_key,
                scale=alt.Scale(domain=[0, umschlag_max], nice=False),
                axis=alt.Axis(format=".2r"),
            ),
            y=alt.Y("Systematik:N", title=None, sort=sort_order).axis(None),
            color=alt.value("#ff7f0e"),
            tooltip=[
                alt.Tooltip(
                    "Value", title=f"{vergleichswert.selected_key}", format=".2f"
                )
            ],
        )
    )

    middle = (
        alt.Chart(chart_data)
        .encode(
            alt.Y("Systematik:N", sort=sort_order).axis(None),
            alt.Text("Systematik:Q"),
        )
        .mark_text()
        .properties(width=20, height=400)
    )

    # Combine the charts
    combined_chart = alt.hconcat(
        bestellpreis_chart.properties(title="Budget", width=300, height=400),
        middle,
        umschlag_chart.properties(
            title=vergleichswert.selected_key, width=300, height=400
        ),
    ).properties(
        title={
            "text": "Top 10 Systematiken: Bestellpreis vs Umschlag",
            "fontSize": 16,
        }
    )

    combined_chart
    return (
        bestellpreis_chart,
        bestellpreis_max,
        chart_data,
        combined_chart,
        middle,
        sort_order,
        top_10,
        top_10_reset,
        umschlag_chart,
        umschlag_max,
    )


@app.cell
def _(mo):
    mo.md(r"""# Budget & Leistung Onleihe""")
    return


@app.cell
def _(mo, pd):
    try:
        onleihe = pd.read_csv(mo.notebook_location() / "public" / "onleihe.csv")
    except:
        onleihe = pd.read_csv(
            "https://raw.githubusercontent.com/a-wendler/bestandskonferenz/refs/heads/main/bestandskonferenz/apps/public/onleihe.csv"
        )

    onleihe["onleihe_2023_2024"] = (
        onleihe["Ausleihen 2023"] + onleihe["Ausleihen 2024"]
    )
    onleihe["Kategorie"] = onleihe["Kategorie"].str.split(" / ").str[0]
    onleihe["Bestellpreis"] = onleihe["Einzelpreis"] * onleihe["Bestand 2024"]

    onleihe_kategorien = onleihe.groupby("Kategorie").agg(
        {
            "Bestand 2024": "sum",
            "Vormerker 2024": "sum",
            "onleihe_2023_2024": "sum",
            "Bestellpreis": "sum",
        }
    )
    onleihe_kategorien["Umschlag 2023/2024"] = (
        onleihe_kategorien["onleihe_2023_2024"]
        / onleihe_kategorien["Bestand 2024"]
        * 0.75
    )

    onleihe_kategorien["Preis pro Entleihung"] = (
        onleihe_kategorien["Bestellpreis"]
        / onleihe_kategorien["onleihe_2023_2024"]
    )
    return onleihe, onleihe_kategorien


@app.cell
def _(mo):
    onleihe_vergleichswert = mo.ui.dropdown(
        {
            "Umschlag 2023/2024": "Umschlag 2023/2024",
            "Ausleihen 2023/2024": "onleihe_2023_2024",
            "Preis pro Entleihung": "Preis pro Entleihung",
            "Bestand 2024": "Bestand 2024",
        },
        value="Umschlag 2023/2024",
    )
    onleihe_vergleichswert
    return (onleihe_vergleichswert,)


@app.cell
def _(alt, onleihe_kategorien, onleihe_vergleichswert, pd):
    # Create a new DataFrame for visualization
    onleihe_chart_data = pd.melt(
        onleihe_kategorien.reset_index(),
        id_vars=["Kategorie"],
        value_vars=["Bestellpreis", onleihe_vergleichswert.value],
        var_name="Metric",
        value_name="Value",
    )

    onleihe_chart_data = onleihe_chart_data[
        onleihe_chart_data["Kategorie"] != "eLearning"
    ]

    # Calculate max values for each metric to set appropriate domains
    onleihe_bestellpreis_max = onleihe_kategorien["Bestellpreis"].max()
    onleihe_umschlag_max = onleihe_kategorien[onleihe_vergleichswert.value].max()

    # Create separate charts for each metric with appropriate domains
    onleihe_bestellpreis_chart = (
        alt.Chart(onleihe_chart_data.query("Metric == 'Bestellpreis'"))
        .mark_bar()
        .encode(
            x=alt.X(
                "Value:Q",
                title="Budget",
                scale=alt.Scale(
                    domain=[0, onleihe_bestellpreis_max], nice=False, reverse=True
                ),
                axis=alt.Axis(format="~s"),
            ),
            y=alt.Y("Kategorie:N", title="Kategorie").axis(None),
            color=alt.value("#1f77b4"),
            tooltip=[alt.Tooltip("Value", title="Budget €", format=".2r")],
        )
    )

    onleihe_umschlag_chart = (
        alt.Chart(
            onleihe_chart_data.query(f"Metric == '{onleihe_vergleichswert.value}'")
        )
        .mark_bar()
        .encode(
            x=alt.X(
                "Value:Q",
                title=onleihe_vergleichswert.selected_key,
                scale=alt.Scale(domain=[0, onleihe_umschlag_max], nice=False),
                axis=alt.Axis(format=".2f"),
            ),
            y=alt.Y("Kategorie:N", title=None).axis(None),
            color=alt.value("#ff7f0e"),
            tooltip=[
                alt.Tooltip("Value", title=onleihe_vergleichswert.selected_key)
            ],
        )
    )

    onleihe_middle = (
        alt.Chart(onleihe_chart_data)
        .encode(
            alt.Y("Kategorie:N").axis(None),
            alt.Text("Kategorie:N"),
        )
        .mark_text()
        .properties(width=130, height=400)
    )

    # Combine the charts
    onleihe_combined_chart = alt.hconcat(
        onleihe_bestellpreis_chart.properties(
            title="Budget", width=300, height=400
        ),
        onleihe_middle,
        onleihe_umschlag_chart.properties(
            title=onleihe_vergleichswert.selected_key, width=300, height=400
        ),
    ).properties(
        title={
            "text": f"Bestellpreis vs {onleihe_vergleichswert.value}",
            "fontSize": 16,
        }
    )

    onleihe_combined_chart
    return (
        onleihe_bestellpreis_chart,
        onleihe_bestellpreis_max,
        onleihe_chart_data,
        onleihe_combined_chart,
        onleihe_middle,
        onleihe_umschlag_chart,
        onleihe_umschlag_max,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
        # Medien in Onleihe & physisch

        In dieser Auswertung kann die Anzahl der ausleihstärksten Medien analysiert werden, die __sowohl in der Onleihe als auch im physischen Bestand__ zu finden sind. Exemplare, Entleihungen und eingesetztes Budget werden analysiert.

        Es werden die Top x Medien ausgewertet, die sowohl online als auch offline verfügbar sind.
        """
    )
    return


@app.cell
def _(mo):
    anzahl_bestleiher = mo.ui.slider(
        50,
        2000,
        50,
        value=1000,
        label="Anzahl der ausgewerteten online und offline verfügbaren Bestleiher auswählen",
        show_value=True,
    )

    anzahl_bestleiher
    return (anzahl_bestleiher,)


@app.cell
def _(anzahl_bestleiher, gesamtdaten, onleihe, pd):
    # Create a proper copy of the merged DataFrame first
    comparison_df = pd.merge(
        gesamtdaten[gesamtdaten["Systematik"] != 200],
        onleihe[onleihe["Format"] != "eAudio"],
        on="Titel",
        suffixes=("_gesamtdaten", "_onleihe"),
    ).copy()

    comparison_df.rename(
        columns={
            "Gesamt": "Loans_gesamtdaten",  # vorher Gesamt
            "Ausleihen gesamt": "Loans_onleihe",
            "exemplare": "Copies_gesamtdaten",
            "Bestand 2024": "Copies_onleihe",
            "Bestellpreis_gesamtdaten": "Price_gesamtdaten",
            "Bestellpreis_onleihe": "Price_onleihe",
        },
        inplace=True,
    )

    # Calculate price per loan using .loc for explicit assignment
    comparison_df.loc[:, "Price_per_Loan_gesamtdaten"] = (
        comparison_df["Price_gesamtdaten"] / comparison_df["Loans_gesamtdaten"]
    )
    comparison_df.loc[:, "Price_per_Loan_onleihe"] = (
        comparison_df["Price_onleihe"] / comparison_df["Loans_onleihe"]
    )

    comparison_df.loc[:, "Loans Sum"] = (
        comparison_df["Loans_onleihe"] + comparison_df["Loans_gesamtdaten"]
    )
    comparison_df = comparison_df.nlargest(anzahl_bestleiher.value, "Loans Sum")
    return (comparison_df,)


@app.cell
def _(mo):
    mo.md(r"""Dieses Diagramm vergleicht die Ausleihzahlen desselben Titels im physischen Bestand und in der Onleihe. Titel oberhalb der roten diagonalen Linie laufen in der Onleihe besser, Titel unterhalb der Linie laufen physisch besser.""")
    return


@app.cell
def _(alt, comparison_df, pd):
    # Calculate the difference between e-book loans and physical book loans
    comparison_df["Loan_Difference"] = (
        comparison_df["Loans_onleihe"] - comparison_df["Loans_gesamtdaten"]
    )

    # Count the number of items above the diagonal line (e-book loans > physical book loans)
    above_line = comparison_df[comparison_df["Loan_Difference"] > 0].shape[0]

    # Count the number of items below the diagonal line (e-book loans < physical book loans)
    below_line = comparison_df[comparison_df["Loan_Difference"] < 0].shape[0]

    # Count the number of items on the diagonal line (e-book loans = physical book loans)
    on_line = comparison_df[comparison_df["Loan_Difference"] == 0].shape[0]

    print(
        f"Number of items above the line (e-books > physical books): {above_line}"
    )
    print(
        f"Number of items below the line (e-books < physical books): {below_line}"
    )
    print(f"Number of items on the line (e-books = physical books): {on_line}")

    # Create a scatter plot comparing loans between formats
    loans_scatter = (
        alt.Chart(comparison_df)
        .mark_circle(size=100)
        .encode(
            x=alt.X("Loans_gesamtdaten:Q", title="Entleihungen physisch"),
            y=alt.Y("Loans_onleihe:Q", title="Entleihungen Onleihe"),
            tooltip=[
                alt.Tooltip("Titel"),
                alt.Tooltip("Loans_gesamtdaten", title="Entleihungen physisch"),
                alt.Tooltip("Loans_onleihe", title="Entleihungen digital"),
            ],
        )
        .properties(
            width=400,
            height=400,
            title="Vergleich der Entleihungen: Physischer Bestand & E-Books (Onleihe)",
        )
    )

    # Add a diagonal line for reference (where values would be equal)
    diagonal = (
        alt.Chart(
            pd.DataFrame(
                {
                    "x": [
                        0,
                        comparison_df[["Loans_gesamtdaten", "Loans_onleihe"]]
                        .max()
                        .max(),
                    ],
                    "y": [
                        0,
                        comparison_df[["Loans_gesamtdaten", "Loans_onleihe"]]
                        .max()
                        .max(),
                    ],
                }
            )
        )
        .mark_line(color="red", strokeDash=[5, 5])
        .encode(x="x", y="y")
    )

    loans_scatter + diagonal
    return above_line, below_line, diagonal, loans_scatter, on_line


@app.cell
def _(mo):
    mo.md(
        """
        Im folgende Diagram werden dieselben top x Titel wie oben getrennt nach physischem Bestand und Onleihe dargestellt.

        Auf der __x-Achse__ ist die Anzahl der __Exemplare__ im Bestand im jeweiligen Format zu sehen.

        Auf der __y-Achse__ ist die Gesamtzahl der __Entleihungen__, die mit diesem Titel erzielt wurde, dargestellt.

        Die __Größe der Punkte__ repräsentiert den Gesamtbetrag, der für den Titel im jeweiligen Format investiert wurde.

        Die Farbe der Punkte zeigt den __Preis pro Ausleihe__.
        """
    )
    return


@app.cell
def _(alt, comparison_df):
    # Calculate the min and max values for the x and y axes across both datasets
    # min_x = min(comparison_df["Copies_gesamtdaten"].min(), comparison_df["Copies_onleihe"].min())
    min_x = 0
    max_x = max(
        comparison_df["Copies_gesamtdaten"].max(),
        comparison_df["Copies_onleihe"].max(),
    )

    min_y = min(
        comparison_df["Loans_gesamtdaten"].min(),
        comparison_df["Loans_onleihe"].min(),
    )
    max_y = max(
        comparison_df["Loans_gesamtdaten"].max(),
        comparison_df["Loans_onleihe"].max(),
    )

    # Create the scatter plot for physical books
    physical_plot = (
        alt.Chart(comparison_df)
        .mark_circle()
        .encode(
            x=alt.X(
                "Copies_gesamtdaten:Q",
                title="Exemplare physisch",
                scale=alt.Scale(domain=[min_x, max_x]),
            ),
            y=alt.Y(
                "Loans_gesamtdaten:Q",
                title="Entleihungen physisch",
                scale=alt.Scale(domain=[min_y, max_y]),
            ),
            size=alt.Size(
                "Price_gesamtdaten:Q",
                scale=alt.Scale(range=[50, 500]),
                legend=alt.Legend(title="Gesamtpreis (€)"),
            ),
            color=alt.Color(
                "Price_per_Loan_gesamtdaten:Q",
                scale=alt.Scale(scheme="turbo"),
                legend=alt.Legend(title="Preis pro Entleihung (€)", format=".2f"),
            ),
            tooltip=[
                alt.Tooltip("Titel"),
                alt.Tooltip("Copies_gesamtdaten", title="Exemplare physisch"),
                alt.Tooltip("Loans_gesamtdaten", title="Entleihungen physisch"),
                alt.Tooltip(
                    "Price_gesamtdaten",
                    title="Gesamtpreis physisch €",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Price_per_Loan_gesamtdaten",
                    title="Preis pro Entleihung €",
                    format=".2f",
                ),
            ],
        )
        .properties(
            width=500,
            height=500,
            title="Physische Bücher: Exemplare, Entleihungen & Preise",
        )
    )

    # Create the scatter plot for e-books
    ebook_plot = (
        alt.Chart(comparison_df)
        .mark_circle()
        .encode(
            x=alt.X(
                "Copies_onleihe:Q",
                title="Exemplare digital",
                scale=alt.Scale(domain=[min_x, max_x]),
            ),
            y=alt.Y(
                "Loans_onleihe:Q",
                title="Entleihungen digital",
                scale=alt.Scale(domain=[min_y, max_y]),
            ),
            size=alt.Size(
                "Price_onleihe:Q",
                scale=alt.Scale(range=[50, 500]),
                legend=alt.Legend(title="Gesamtpreis (€)"),
            ),
            color=alt.Color(
                "Price_per_Loan_onleihe:Q",
                scale=alt.Scale(scheme="turbo"),
                legend=alt.Legend(title="Preis pro Entleihung (€)", format=".2f"),
            ),
            tooltip=[
                alt.Tooltip("Titel"),
                alt.Tooltip("Copies_onleihe", title="Exemplare digital"),
                alt.Tooltip("Loans_onleihe", title="Entleihungen digital"),
                alt.Tooltip(
                    "Price_onleihe", title="Gesamtpreis digital €", format="(.2f"
                ),
                alt.Tooltip(
                    "Price_per_Loan_onleihe",
                    title="Preis pro Entleihung €",
                    format="(.2f",
                ),
            ],
        )
        .properties(
            width=500,
            height=500,
            title="E-Books: Exemplare, Entleihungen & Preise",
        )
    )

    # Combine the plots side by side
    scatter_combined_plot = alt.hconcat(
        physical_plot.interactive(), ebook_plot.interactive()
    ).resolve_scale(
        color="independent",
        size="shared",  # Ensure uniform scaling of size between the two plots
    )

    scatter_combined_plot
    return (
        ebook_plot,
        max_x,
        max_y,
        min_x,
        min_y,
        physical_plot,
        scatter_combined_plot,
    )


@app.cell
def _(comparison_df, pd):
    # Aggregate sum for physical books
    physical_summary = {
        "Ausleihen 2023/24": comparison_df["Loans_gesamtdaten"].sum(),
        "Exemplare": comparison_df["Copies_gesamtdaten"].sum(),
        "Gesamtpreis": comparison_df["Price_gesamtdaten"].sum(),
    }

    # Aggregate sum for e-books
    ebook_summary = {
        "Ausleihen 2023/24": comparison_df["Loans_onleihe"].sum(),
        "Exemplare": comparison_df["Copies_onleihe"].sum(),
        "Gesamtpreis": comparison_df["Price_onleihe"].sum(),
    }
    # Create a DataFrame for the summary
    summary_table = pd.DataFrame(
        {"Physische Bücher": physical_summary, "E-Books": ebook_summary}
    )

    # Transpose the table for better readability
    summary_table = summary_table.T

    # Format the numbers for German conventions
    summary_table["Gesamtpreis"] = summary_table["Gesamtpreis"].apply(
        lambda x: f"€{x:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    summary_table["Ausleihen 2023/24"] = summary_table["Ausleihen 2023/24"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".")
    )
    summary_table["Exemplare"] = summary_table["Exemplare"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".")
    )

    summary_table
    return ebook_summary, physical_summary, summary_table


if __name__ == "__main__":
    app.run()
