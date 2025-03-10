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
    df = pd.concat(
        [
            pd.read_csv(
                mo.notebook_location() / file,
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
    mo.md("""# Entwicklung allgmeiner Leistungszahlen""")
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
def _(pd):
    buchdaten = pd.read_csv("buchdaten.csv")
    buchdaten["exemplare"] = buchdaten.groupby("katkey")["katkey"].transform(
        "count"
    )

    bestelldaten = pd.read_csv(
        "bestelldaten.csv", sep=";", encoding="latin_1", decimal=",", thousands="."
    )
    bestelldaten["Bestellpreis"] = pd.to_numeric(
        bestelldaten["Bestellpreis"], errors="ignore"
    )

    buchdaten_grouped = buchdaten.groupby("katkey", as_index=False).agg(
        {
            "Geistiger Schöpfer": "first",
            "Schlagwort": "first",
            "Signatur": "first",
            "2. Signatur": "first",
            "Gesamt": "sum",
            "lfd. Jahr": "sum",
            "Vor-Jahr": "sum",
            "VorVor-Jahr": "sum",
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
    gesamtdaten = gesamtdaten.rename(
        columns={"lfd. Jahr": "2025", "Vor-Jahr": "2024", "VorVor-Jahr": "2023"}
    )
    return (
        bestelldaten,
        bestelldaten_grouped,
        buchdaten,
        buchdaten_grouped,
        gesamtdaten,
    )


@app.cell
def _(gesamtdaten):
    umsatz_systematik = gesamtdaten.groupby("Systematik").agg(
        {
            "exemplare": "sum",
            "Gesamt": "sum",
            "2023": "sum",
            "2024": "sum",
            "2025": "sum",
            "Bestellpreis": "sum",
        }
    )
    umsatz_systematik["Umschlag"] = (
        umsatz_systematik["2024"] / umsatz_systematik["exemplare"]
    )
    umsatz_systematik["Preis pro Entleihung"] = (
        umsatz_systematik["Bestellpreis"] / umsatz_systematik["2024"]
    )
    return (umsatz_systematik,)


@app.cell
def _(mo):
    mo.md(r"""# Budget vs. Leistung""")
    return


@app.cell
def _(mo):
    vergleichswert = mo.ui.dropdown(
        {"Umschlag":"Umschlag", "Gesamtentleihungen":"Gesamt", "Entleihungen 2024":"2024", "Entleihungen 2025":"2025", "Preis pro Entleihung":"Preis pro Entleihung", "Exemplare im Bestand":"exemplare"},
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
            y=alt.Y("Systematik:N", title="Systematik", sort=sort_order),
            color=alt.value("#1f77b4"),
        )
    )

    umschlag_chart = (
        alt.Chart(chart_data.query(f"Metric == '{vergleichswert.value}'"))
        .mark_bar()
        .encode(
            x=alt.X(
                "Value:Q",
                title=vergleichswert.value,
                scale=alt.Scale(domain=[0, umschlag_max], nice=False),
                axis=alt.Axis(format=".2f"),
            ),
            y=alt.Y("Systematik:N", title=None, sort=sort_order),
            color=alt.value("#ff7f0e"),
        )
    )

    # Combine the charts
    combined_chart = alt.hconcat(
        bestellpreis_chart.properties(title="Bestellpreis", width=300, height=400),
        umschlag_chart.properties(
            title=vergleichswert.value, width=300, height=400
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
        sort_order,
        top_10,
        top_10_reset,
        umschlag_chart,
        umschlag_max,
    )


@app.cell
def _(mo):
    mo.md(r"""# Online - Offline""")
    return


@app.cell
def _(pd):
    onleihe = pd.read_excel("onleihe.xlsx")
    onleihe
    onleihe["Kategorie"] = onleihe["Kategorie"].str.split(" / ").str[0]
    onleihe["Bestellpreis"] = onleihe["Einzelpreis"] * onleihe["Bestand 2024"]
    return (onleihe,)


@app.cell
def _(onleihe):
    onleihe_kategorien = onleihe.groupby("Kategorie").agg(
        {
            "Bestand 2024": "sum",
            "Vormerker 2024": "sum",
            "Ausleihen 2022": "sum",
            "Ausleihen 2023": "sum",
            "Ausleihen 2024": "sum",
            "Ausleihen gesamt": "sum",
            "Bestellpreis": "sum",
        }
    )
    onleihe_kategorien["Umschlag 2024"] = (
        onleihe_kategorien["Ausleihen 2024"] / onleihe_kategorien["Bestand 2024"] * .75
    )

    onleihe_kategorien["Preis pro Entleihung"] = (
        onleihe_kategorien["Bestellpreis"] / onleihe_kategorien["Ausleihen 2024"]
    )
    return (onleihe_kategorien,)


@app.cell
def _(mo):
    onleihe_vergleichswert = mo.ui.dropdown(
        [
            "Umschlag 2024",
            "Ausleihen gesamt",
            "Ausleihen 2022",
            "Ausleihen 2023",
            "Ausleihen 2024",
            "Preis pro Entleihung",
            "Bestand 2024"
        ],
        value="Umschlag 2024",
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
            y=alt.Y("Kategorie:N", title="Kategorie"),
            color=alt.value("#1f77b4"),
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
                title=onleihe_vergleichswert.value,
                scale=alt.Scale(domain=[0, onleihe_umschlag_max], nice=False),
                axis=alt.Axis(format=".2f"),
            ),
            y=alt.Y("Kategorie:N", title=None),
            color=alt.value("#ff7f0e"),
        )
    )

    # Combine the charts
    onleihe_combined_chart = alt.hconcat(
        onleihe_bestellpreis_chart.properties(
            title="Bestellpreis", width=300, height=400
        ),
        onleihe_umschlag_chart.properties(
            title=onleihe_vergleichswert.value, width=300, height=400
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
        onleihe_umschlag_chart,
        onleihe_umschlag_max,
    )


@app.cell
def _(mo):
    mo.md(r"""# Bestleiher 2024""")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
