import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium", app_title="LSB Bestandskonferenz")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    import numpy as np


    # Helper function for loading files with fallback to GitHub
    def load_file(file_path, is_remote=False, **kwargs):
        """
        Load a file with fallback to GitHub repository.

        Args:
            file_path: Local path or file name
            is_remote: If True, directly use GitHub URL
            **kwargs: Arguments to pass to pd.read_csv

        Returns:
            DataFrame with loaded data
        """
        try:
            if is_remote:
                return pd.read_csv(
                    f"https://raw.githubusercontent.com/a-wendler/bestandskonferenz/refs/heads/main/bestandskonferenz/apps/public/{file_path}",
                    **kwargs,
                )
            else:
                return pd.read_csv(
                    mo.notebook_location() / "public" / file_path, **kwargs
                )
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            # Fallback to GitHub if local loading fails
            if not is_remote:
                return pd.read_csv(
                    f"https://raw.githubusercontent.com/a-wendler/bestandskonferenz/refs/heads/main/bestandskonferenz/apps/public/{file_path}",
                    **kwargs,
                )
            else:
                raise
    return alt, load_file, mo, np, pd


@app.cell
def _():
    # """
    # Transform cumulative data files to absolute values.
    # This function processes the cumulative data files and
    # saves them as absolute value files.
    # """

    # transform_files = [
    #     "2017-kummulativ.csv",
    #     "2018-kummulativ.csv",
    #     "2019-kummulativ.csv",
    #     "2020-kummulativ.csv",
    #     "2021-kummulativ.csv",
    #     "2022-kummulativ.csv",
    #     "2023-kummulativ.csv",
    #     "2024-kummulativ.csv",
    # ]

    # # Track processed files
    # processed_output_files = []
    # transform_cols = ["Entleihungen", "Besucher", "aktivierte Ausweise"]
    # last_df = None

    # # Process each file to create absolute value files if they don't exist
    # for curr_file in transform_files:
    #     output_file = f"{curr_file[:4]}-absolut.csv"
    #     processed_output_files.append(output_file)

    #     # Check if file already exists (avoiding reprocessing)
    #     try:
    #         # Load cumulative data
    #         last_df = load_file(curr_file, parse_dates=["Zeitraum"])

    #         # Calculate absolute values per library
    #         last_df[transform_cols] = (
    #             last_df.groupby("Bibliothek")[transform_cols]
    #             .diff()
    #             .fillna(last_df[transform_cols])
    #         )

    #         # Format output and save
    #         last_df["Zeitraum"] = last_df["Zeitraum"].dt.strftime("%Y-%m")
    #         last_df.sort_values(["Zeitraum", "Bibliothek"]).to_csv(
    #             mo.notebook_location() / "public" / output_file,
    #             index=False,
    #             encoding="utf-8",
    #         )
    #         print(f"Generated {output_file}")
    #     except Exception as e:
    #         print(f"Error processing {curr_file}: {e}")

    # Return all variables needed by other cells
    # return (
    #     curr_file,
    #     last_df,
    #     output_file,
    #     processed_output_files,
    #     transform_cols,
    #     transform_files,
    # )
    return


@app.cell
def _(mo):
    mo.md(
        """
        # Statistiken zur Bestandskonferenz 2025
        ## Vorbemerkung

        In dieses Dashboard wurden nur statistische Vergleiche aufgenommen, die statistisch hochsignifikant und robust sind. Dazu wurden statistische Korrekturen in die Daten eingerechnet, etwa um den unterschiedlichen Leihfristen in Onleihe und im physischen Bestand gerecht zu werden. Bei jeder Analyse ist im Einzelnen aufgeführt, woher die Zahlen kommen, wie berechnet wurde und welche Korrekturen vorgenommen wurden. Ihre Fragen zum Dashboard beantworten Sebastian Wallwitz, Annett Helbig & André Wendler.
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""# Entwicklung allgemeiner Leistungszahlen""")
    return


@app.cell(hide_code=True)
def _(mo, monthly_df):
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
            "Entleihungen",
            "Besucher",
        ],
        label="Auswertungsdimension",
        value="Entleihungen",
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
                monthly_df.index.min().strftime("%Y-%m-%d"),
                monthly_df.index.max().strftime("%Y-%m-%d"),
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
    dimension,
    mo,
    monthly_df,
    online_auswahl,
    pd,
    trendlinie,
    z_scores,
    zeitfilter,
):
    # Filter data for libraries and online services
    library_data = monthly_df[
        (monthly_df.index >= zeitfilter.value[0].strftime("%Y-%m-%d"))
        & (monthly_df.index <= zeitfilter.value[1].strftime("%Y-%m-%d"))
        & monthly_df["Bibliothek"].isin(bibliotheks_auswahl.value)
    ]
    online_data = monthly_df[
        (monthly_df.index >= zeitfilter.value[0].strftime("%Y-%m-%d"))
        & (monthly_df.index <= zeitfilter.value[1].strftime("%Y-%m-%d"))
        & monthly_df["Bibliothek"].isin(online_auswahl.value)
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

    final_chart = final_chart.properties(
        title=f"{dimension.value} für Bibliotheken und Online-Dienste",
        width=850,
    )

    mo.center(final_chart)
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
        __Standardisierte Werte__ bedeutet, dass im Diagramm nicht die absoluten Werte, sondern die Abweichungen vom Durchschnitt des gesamten Vergleichszeitraums angegeben werden. Dadurch lässt sich die Performance von Bibliotheken und Online-Diensten direkt vergleichen ungeachtet der absoluten Werte.

        Z-Score über 0 bedeutet: überdurchschnittliches Wachstum, 0 = durchschnittliches Wachstum, unter 0 = Wachstum unter dem Durchschnitt (Rückgang). Ein Z-Score von -0,5 entspricht ungefähr dem 31. Perzentil. Das bedeutet, dass etwa 31 % der Daten in der Verteilung unter diesem Wert liegen und 69 % darüber. Werte über oder unter einem Z-Score von +/- 1 sind bereits sehr deutliche Abweichungen, bei denen nur noch 16 % der Werte noch weiter außerhalb der Verteilung liegen.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""Die Zahlen visualisieren unsere bekannten Monatsstatistiken hier nur neu.""")
    return


@app.cell(hide_code=True)
def _():
    systematik_descriptions = {
        79: "ePaper (Genios)",
        80: "eBook (Onleihe)",
        81: "eAudio (Onleihe)",
        82: "eVideo (Onleihe)",
        83: "eMusic (Onleihe)",
        84: "ePaper (Onleihe)",
        85: "eMagazin (Onleihe)",
        86: "eVideo (Filmfriend)",
        87: "eAudio (Overdrive)",
        88: "eVideo (Overdrive)",
        89: "eBook (Overdrive)",
        100: "Belletristik Erw",
        110: "Belletristik Jugend",
        120: "Belletristik REG",
        130: "Belletristik Kinder",
        140: "Belletristik Musik",
        200: "CD Belletristik",
        210: "CD KAB",
        220: "CD Kinder",
        230: "CD Jugend",
        240: "CD Musik",
        300: "CD-Rom Belletristik",
        310: "CD-Rom KAB",
        320: "CD-Rom Jugend",
        330: "CD-Rom Kinder",
        340: "CD-Rom Musik",
        400: "DVD Belletristik",
        410: "DVD KAB",
        420: "DVD Jugend",
        430: "DVD Kinder",
        440: "DVD Musik",
        500: "eMedium Erwachsene",
        510: "eMedium Kinder",
        520: "eMedium Jugend",
        540: "eMedium Musik",
        600: "Fachliteratur Erwachsene",
        610: "Fachliteratur Jugend",
        620: "Fachliteratur Musik",
        630: "Fachliteratur Kinder",
        640: "Fachlit Erwachsene Demokratie",
        800: "Medienkombination Belletristik Erw.",
        810: "Medienkombination KAB",
        820: "Medienkombination Musik",
        830: "Medienkombination REG",
        840: "Medienkombination Kinder",
        900: "Noten",
        1000: "Spiele",
        1100: "Videokassette",
        1200: "Zeitschriften Erwachsene",
        1210: "Zeitschriften Jugend",
        1220: "Zeitschriften Kinder",
        1230: "Zeitschriften Musik",
        1300: "Dias",
        1400: "Film",
        1500: "Grafik (Artothek)",
        1600: "Schallplatte",
        1700: "Verschiedenes (außer Kibi + Mubi)",
        1710: "Verschiedenes Mubi",
        1720: "Verschiedenes Kibi",
        1730: "Verschiedenes Gegenstand (BdD)",
        1800: "TonbandKassette",
        2000: "Online-Dokument",
        9001: "Summe I (Belletristik)",
        9002: "Summe II (Kinderliteratur)",
        9003: "Summe III (Fachliteratur)",
        9005: "Summe V (Zeitschriften)",
        9010: "Summe IV CD",
        9011: "Summe IV CDRom",
        9012: "Summe IV DVD",
        9013: "Summe IV MedienKomb",
        9014: "Summe IV eMedien",
        9015: "Summe Verschiedenes",
    }
    return (systematik_descriptions,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Budget & Leistung physischer Bestand

        Die Frage hinter den folgenden beiden Grafiken lautete: stimmt das Verhältnis zwischen Input & Output, d. h. investieren wir den Erwerbungsetat so, dass die Investition die Leipziger Bürgerschaft optimal erreicht. Als Grundlage dienten die Erwerbungsdaten aus 2023 und 2024. Diese Daten wurden mit den Entleihdaten aus den beiden Jahren verschnitten. Man kann so die 10 Systematiken, in die wir das meiste Geld investieren, ihren Leistungszahlen gegenüberstellen.

        Idealerweise sollte das Bestandssegment mit dem höchsten Investment auch die besten Leistungszahlen erbringen.

        Es sind hier immer die Budget- und Leistungszahlen von 2023 & 2024 gemeinsam verwendet, um Sondereffekte eines der beiden Jahre statistisch zu glätten. Die Zahlen sind als Kennzahlen und nicht als reale Zahlen zu betrachten, weil hier nur solche Titel berücksichtigt werden, für die 2023 oder 2024 Exemplare beschafft wurden. Bei den Entleihungen werden aber auch in Vorjahren beschaffte Exemplare berücksichtigt, nicht allerdings beim Budget. Deshalb entsprechen die Umschlagszahlen nur im Verhältnis zueinander aber nicht absolut denjenigen aus der Monatsstatistik.
        """
    )
    return


@app.cell
def _(load_file, pd):
    jahre = ["2023", "2024"]

    # Define column selection for efficiency
    buchdaten_columns = [
        "Zweigstelle",
        "Abteilung",
        "Geistiger Schöpfer",
        "Gesamt",
        "2024",
        "2023",
        "Titel",
        "Mediennummer",
        "Erscheinungsjahr",
        "Systematik",
        "katkey",
    ]

    # Load both datasets with consolidated function
    buchdaten = load_file(
        "buchdaten_gesamt_reduce.csv",
        usecols=buchdaten_columns,
        low_memory=False,
    )

    # Load and concatenate bestelldaten in one step
    bestelldaten = pd.concat(
        [
            load_file(
                f"bestelldaten_{jahr}.csv",
                sep=";",
                encoding="latin_1",
                decimal=",",
                thousands=".",
                low_memory=False,
            )
            for jahr in jahre
        ]
    )

    # Process buchdaten in a consolidated manner
    buchdaten["exemplare"] = buchdaten.groupby("katkey")["katkey"].transform(
        "count"
    )
    buchdaten["2023_2024"] = buchdaten["2023"] + buchdaten["2024"]

    # Convert to numeric upfront to avoid mixed type operations
    bestelldaten["Bestellpreis"] = pd.to_numeric(
        bestelldaten["Bestellpreis"], errors="coerce"
    )

    # Group buchdaten by katkey
    buchdaten_grouped = buchdaten.groupby("katkey", as_index=False).agg(
        {
            "Geistiger Schöpfer": "first",
            "Gesamt": "sum",
            "2023_2024": "sum",
            "Titel": "first",
            "Mediennummer": "first",
            "Erscheinungsjahr": "first",
            "Systematik": "first",
            "exemplare": "first",
        }
    )

    # Group bestelldaten by katkey
    bestelldaten_grouped = bestelldaten.groupby("katkey", as_index=False).agg(
        {"EXEMPLARANZ": "sum", "Bestellpreis": "sum"}
    )

    # Merge datasets once
    gesamtdaten = pd.merge(
        buchdaten_grouped, bestelldaten_grouped, on="katkey", how="left"
    )
    gesamtdaten = gesamtdaten[gesamtdaten["katkey"] != 1952225]

    # FIXED: Calculate Durchschnittspreis_pro_Exemplar more comprehensively
    # Instead of restricting to only rows where EXEMPLARANZ > 0, we need a different approach

    # Step 1: Calculate the per-exemplar price where we have EXEMPLARANZ data
    valid_exemplar_mask = gesamtdaten["EXEMPLARANZ"] > 0

    # For valid rows, calculate price per exemplar
    gesamtdaten.loc[valid_exemplar_mask, "Durchschnittspreis_pro_Exemplar"] = (
        gesamtdaten.loc[valid_exemplar_mask, "Bestellpreis"]
        / gesamtdaten.loc[valid_exemplar_mask, "EXEMPLARANZ"]
    )

    # Step 2: For rows without valid EXEMPLARANZ, calculate a default price
    # This better matches the original calculation logic

    # Get the average price per category
    systematik_preise = (
        gesamtdaten[valid_exemplar_mask]
        .groupby("Systematik")["Durchschnittspreis_pro_Exemplar"]
        .mean()
    )

    # Apply this average to rows with missing prices
    for systematik, preis in systematik_preise.items():
        systematik_mask = (gesamtdaten["Systematik"] == systematik) & (
            ~valid_exemplar_mask
        )
        gesamtdaten.loc[systematik_mask, "Durchschnittspreis_pro_Exemplar"] = preis

    # Fill any remaining NAs with overall mean price
    overall_mean_price = gesamtdaten.loc[
        valid_exemplar_mask, "Durchschnittspreis_pro_Exemplar"
    ].mean()
    gesamtdaten["Durchschnittspreis_pro_Exemplar"] = gesamtdaten[
        "Durchschnittspreis_pro_Exemplar"
    ].fillna(overall_mean_price)

    # Calculate average price per systematic group
    gesamtdaten["Durchschnittlicher_Einzelbestellpreis"] = gesamtdaten.groupby(
        "Systematik"
    )["Durchschnittspreis_pro_Exemplar"].transform("mean")

    # Budget calculation
    gesamtdaten["budget_hochrechnung"] = (
        gesamtdaten["Durchschnittlicher_Einzelbestellpreis"]
        * gesamtdaten["exemplare"]
    )

    # Return all needed variables for subsequent cells
    return (
        bestelldaten,
        bestelldaten_grouped,
        buchdaten,
        buchdaten_columns,
        buchdaten_grouped,
        gesamtdaten,
        jahre,
        overall_mean_price,
        preis,
        systematik,
        systematik_mask,
        systematik_preise,
        valid_exemplar_mask,
    )


@app.cell
def _(gesamtdaten):
    umsatz_systematik = gesamtdaten.groupby("Systematik").agg(
        {
            "exemplare": "sum",
            "Gesamt": "sum",
            "2023_2024": "sum",
            "budget_hochrechnung": "sum",
            "Bestellpreis": "sum",
        }
    )
    umsatz_systematik["Umschlag 2023/24"] = (
        umsatz_systematik["2023_2024"] / umsatz_systematik["exemplare"] / 2
    )
    umsatz_systematik["Preis pro Entleihung"] = (
        umsatz_systematik["budget_hochrechnung"] / umsatz_systematik["Gesamt"]
    )
    return (umsatz_systematik,)


@app.cell
def _(mo):
    vergleichswert = mo.ui.dropdown(
        {
            "Umschlag 2023/24": "Umschlag 2023/24",
            "Entleihungen 2023/2024 ": "2023_2024",
            "Gesamtentleihungen": "Gesamt",
            "Preis pro Entleihung": "Preis pro Entleihung",
            "Exemplare im Bestand": "exemplare",
        },
        value="Umschlag 2023/24",
    )
    mo.vstack(
        [
            mo.md(
                "__Wählen Sie einen Wert, der dem Budget gegenübergestellt werden soll.__"
            ),
            vergleichswert,
        ]
    )
    return (vergleichswert,)


@app.cell
def _(
    alt,
    mo,
    pd,
    systematik_descriptions,
    umsatz_systematik,
    vergleichswert,
):
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

    # Create a DataFrame for the middle chart with codes and descriptions
    middle_data = pd.DataFrame(
        {
            "Systematik": sort_order,
            "Label": [
                f"{code} - {systematik_descriptions.get(code, 'Unbekannt')}"
                for code in sort_order
            ],
        }
    )

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
            color=alt.value("#269e58"),
            tooltip=[
                alt.Tooltip(
                    "Value", title=f"{vergleichswert.selected_key}", format=".2f"
                )
            ],
        )
    )

    middle = (
        alt.Chart(middle_data)
        .encode(
            alt.Y("Systematik:N", sort=sort_order).axis(None),
            alt.Text("Label:N"),
        )
        .mark_text(align="center")
        .properties(
            width=200, height=400
        )  # Increased width to accommodate longer text
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
            "text": f"Top 10 Systematiken: Budget & {vergleichswert.selected_key}",
            "fontSize": 16,
        }
    )

    mo.center(combined_chart)
    return (
        bestellpreis_chart,
        bestellpreis_max,
        chart_data,
        combined_chart,
        middle,
        middle_data,
        sort_order,
        top_10,
        top_10_reset,
        umschlag_chart,
        umschlag_max,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
        # Budget & Leistung Onleihe

        Die Zahlen für den Umschlag wurden so korrigiert, als ob in der Onleihe auch eine Ausleihfrist von 4 Wochen bestünde.
        """
    )
    return


@app.cell
def _(load_file):
    # Load Onleihe data with consolidated function
    onleihe = load_file("onleihe.csv")

    # Perform all data transformations in a single block
    onleihe["onleihe_2023_2024"] = (
        onleihe["Ausleihen 2023"] + onleihe["Ausleihen 2024"]
    )
    onleihe["Kategorie"] = onleihe["Kategorie"].str.split(" / ").str[0]
    onleihe["Bestellpreis"] = (
        onleihe["Einzelpreis"] * onleihe["Bestand 2024"] * 1.2
    )
    onleihe["Bestand 2024"] = onleihe["Bestand 2024"] * 1.2

    # Group by category once
    onleihe_kategorien = onleihe.groupby("Kategorie").agg(
        {
            "Bestand 2024": "sum",
            "Vormerker 2024": "sum",
            "onleihe_2023_2024": "sum",
            "Bestellpreis": "sum",
        }
    )

    # Apply calculated fields at once
    onleihe_kategorien["Umschlag 2023/2024"] = (
        onleihe_kategorien["onleihe_2023_2024"]
        / onleihe_kategorien["Bestand 2024"]
        * 0.75
    )

    # Avoid division by zero errors
    onleihe_valid_rows = onleihe_kategorien["onleihe_2023_2024"] > 0
    onleihe_kategorien.loc[onleihe_valid_rows, "Preis pro Entleihung"] = (
        onleihe_kategorien.loc[onleihe_valid_rows, "Bestellpreis"]
        / onleihe_kategorien.loc[onleihe_valid_rows, "onleihe_2023_2024"]
    )
    return onleihe, onleihe_kategorien, onleihe_valid_rows


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
    mo.vstack(
        [
            mo.md(
                "__Wählen Sie einen Wert, der dem Budget gegenübergestellt werden soll.__"
            ),
            onleihe_vergleichswert,
        ]
    )
    return (onleihe_vergleichswert,)


@app.cell
def _(alt, mo, onleihe_kategorien, onleihe_vergleichswert, pd):
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
            color=alt.value("#269e58"),
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
            "text": f"Bestellpreis & {onleihe_vergleichswert.value}",
            "fontSize": 16,
        }
    )

    mo.center(onleihe_combined_chart)
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
        # Direktvergleich Onleihe & physisch

        __Frage: wie schneiden Medien im direkten Vergleich ab, wenn Sie sowohl online als auch offline verfügbar sind?__


        In dieser Auswertung kann die Anzahl der ausleihstärksten Medien analysiert werden, die __sowohl in der Onleihe als auch im physischen Bestand__ zu finden sind. Exemplare, Entleihungen und eingesetztes Budget werden analysiert.

        Es werden die Top x Titel ausgewertet, die sowohl online als auch offline verfügbar sind.

        Die Zahl der Exemplare in der Onleihe wurde korrigiert, um nachgekaufte Lizenzen mitzubedenken. Außerdem wurde die Umschlagszahl der Onleihe so korrigiert, als wären die Medien dort auch für 4 Wochen entleihbar.

        Im Gegensatz zur Budgetvergleichsanalyse oben wurden hier die Kosten des Bestandes auch auf die Exemplare hochgerechnet, die vor 2023 angeschafft wurden, um auch diese Longrunner mit den nicht verschleißenden Lizenzen in der Onleihe besser vergleichen zu können.

        Hörbücher wurden aus beiden Beständen herausgerechnet, weil sie die Vergleichbarkeit pro Titel erschwert hätten.
        """
    )
    return


@app.cell
def _(mo):
    anzahl_bestleiher = mo.ui.slider(
        50,
        3200,
        50,
        value=1000,
        label="Anzahl der ausgewerteten online und offline verfügbaren Bestleiher auswählen",
        show_value=True,
    )

    anzahl_bestleiher
    return (anzahl_bestleiher,)


@app.cell
def _(anzahl_bestleiher, gesamtdaten, onleihe, pd):
    # Filter data before merge to reduce memory usage
    # Remove hörbücher from both datasets as mentioned in the explanation
    gesamtdaten_filtered = gesamtdaten[gesamtdaten["Systematik"] != 200].copy()
    onleihe_filtered = onleihe[onleihe["Format"] != "eAudio"].copy()

    # Create a proper copy of the merged DataFrame with only needed columns
    # This reduces memory usage by not carrying all columns forward
    comparison_df = pd.merge(
        gesamtdaten_filtered[
            [
                "Titel",
                "Gesamt",
                "exemplare",
                "Systematik",
                "budget_hochrechnung",
                "Bestellpreis",
                "EXEMPLARANZ",
            ]
        ],
        onleihe_filtered[
            ["Titel", "Ausleihen gesamt", "Bestand 2024", "Bestellpreis"]
        ],
        on="Titel",
        suffixes=("_gesamtdaten", "_onleihe"),
    )

    # Rename columns in a single step
    comparison_column_mapping = {
        "Gesamt": "Loans_gesamtdaten",
        "Ausleihen gesamt": "Loans_onleihe",
        "exemplare": "Copies_gesamtdaten",
        "Bestand 2024": "Copies_onleihe",
        "Bestellpreis_gesamtdaten": "Price_gesamtdaten",
        "Bestellpreis_onleihe": "Price_onleihe",
    }
    comparison_df.rename(columns=comparison_column_mapping, inplace=True)

    # Remove data with missing information
    comparison_df = comparison_df[comparison_df["Systematik"] != 200]

    # Create mask for valid data to avoid division by zero
    comparison_valid_gesamtdaten = comparison_df["Loans_gesamtdaten"] > 0
    comparison_valid_onleihe = comparison_df["Loans_onleihe"] > 0

    # Calculate price per loan in a safe way
    comparison_df.loc[
        comparison_valid_gesamtdaten, "Price_per_Loan_gesamtdaten"
    ] = (
        comparison_df.loc[comparison_valid_gesamtdaten, "budget_hochrechnung"]
        / comparison_df.loc[comparison_valid_gesamtdaten, "Loans_gesamtdaten"]
    )

    comparison_df.loc[comparison_valid_gesamtdaten, "Price_per_Loan_real"] = (
        comparison_df.loc[comparison_valid_gesamtdaten, "Price_gesamtdaten"]
        / comparison_df.loc[comparison_valid_gesamtdaten, "Loans_gesamtdaten"]
    )

    comparison_df.loc[comparison_valid_onleihe, "Price_per_Loan_onleihe"] = (
        comparison_df.loc[comparison_valid_onleihe, "Price_onleihe"]
        / comparison_df.loc[comparison_valid_onleihe, "Loans_onleihe"]
    )

    # Calculate total loans and filter for top titles
    comparison_df["Loans Sum"] = (
        comparison_df["Loans_onleihe"] + comparison_df["Loans_gesamtdaten"]
    )
    comparison_df = comparison_df.nlargest(anzahl_bestleiher.value, "Loans Sum")

    # Price correction for items acquired before 2023 - as per original code
    # Create mask and apply correction in one pass
    comparison_mask = (
        comparison_df["Copies_gesamtdaten"] > comparison_df["EXEMPLARANZ"]
    ) & (comparison_df["Price_gesamtdaten"] != 0)

    if (
        comparison_mask.any()
    ):  # Only apply if there are rows matching the condition
        comparison_df.loc[comparison_mask, "Price_gesamtdaten"] = (
            comparison_df.loc[comparison_mask, "Copies_gesamtdaten"]
            * (
                comparison_df.loc[comparison_mask, "Price_gesamtdaten"]
                / comparison_df.loc[comparison_mask, "EXEMPLARANZ"]
            )
        )

    # Final filtering to remove rows with zero prices
    comparison_df = comparison_df[comparison_df["Price_gesamtdaten"] != 0]

    # Drop unnecessary columns to save memory
    comparison_df = comparison_df.drop(columns=["EXEMPLARANZ"], errors="ignore")
    return (
        comparison_column_mapping,
        comparison_df,
        comparison_mask,
        comparison_valid_gesamtdaten,
        comparison_valid_onleihe,
        gesamtdaten_filtered,
        onleihe_filtered,
    )


@app.cell
def _(mo):
    mo.md(r"""Dieses Diagramm vergleicht die Ausleihzahlen desselben Titels im physischen Bestand und in der Onleihe. Titel oberhalb der roten diagonalen Linie laufen in der Onleihe besser, Titel unterhalb der Linie laufen physisch besser.""")
    return


@app.cell
def _(alt, comparison_df, mo, pd):
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

    mo.center(loans_scatter + diagonal)
    return above_line, below_line, diagonal, loans_scatter, on_line


@app.cell
def _(mo):
    mo.md(
        """
        Im folgenden Diagramm werden dieselben top x Titel wie oben getrennt nach physischem Bestand und Onleihe dargestellt.

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
        alt.Chart(comparison_df[comparison_df["Price_gesamtdaten"].notnull()])
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
                "Price_per_Loan_real:Q",
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
                    "Price_per_Loan_real",
                    title="Preis pro Entleihung €",
                    format=".2f",
                ),
            ],
        )
        .properties(
            width=400,
            height=400,
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
            ],
        )
        .properties(
            width=400,
            height=400,
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
def _(anzahl_bestleiher, mo):
    mo.md(
        f"""
    ## Zusammenfassung der {anzahl_bestleiher.value} Medien aus physischem Bestand und Onleihe
          """
    )
    return


@app.cell
def _(comparison_df, pd):
    # Calculate aggregated metrics in a single step
    physical_summary = {
        "Ausleihen gesamt": comparison_df["Loans_gesamtdaten"].sum(),
        "Exemplare": comparison_df["Copies_gesamtdaten"].sum(),
        "Gesamtpreis": comparison_df["budget_hochrechnung"].sum(),
    }

    ebook_summary = {
        "Ausleihen gesamt": comparison_df["Loans_onleihe"].sum(),
        "Exemplare": comparison_df["Copies_onleihe"].sum(),
        "Gesamtpreis": comparison_df["Price_onleihe"].sum(),
    }

    # Create DataFrame directly with both columns
    summary_table = pd.DataFrame(
        {"Physischer Bestand": physical_summary, "E-Books": ebook_summary}
    ).T

    # Calculate price per loan (safely handling division)
    summary_table["Preis pro Entleihung"] = (
        summary_table["Gesamtpreis"] / summary_table["Ausleihen gesamt"]
    )


    # Define formatting function
    def format_summary_number(x, is_price=False):
        if is_price:
            return (
                f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        else:
            return f"{x:,.0f}".replace(",", ".")


    # Apply formatting
    summary_table["Gesamtpreis"] = summary_table["Gesamtpreis"].apply(
        lambda x: format_summary_number(x, is_price=True)
    )
    summary_table["Ausleihen gesamt"] = summary_table["Ausleihen gesamt"].apply(
        format_summary_number
    )
    summary_table["Exemplare"] = summary_table["Exemplare"].apply(
        format_summary_number
    )
    summary_table["Preis pro Entleihung"] = summary_table[
        "Preis pro Entleihung"
    ].apply(lambda x: f"€ {x:.2f}".replace(".", ","))

    summary_table
    # Return all variables for marimo to track
    return (
        ebook_summary,
        format_summary_number,
        physical_summary,
        summary_table,
    )


@app.cell
def _(load_file, pd):
    # Define file list for monthly data loading
    monthly_files = [
        "2017-absolut.csv",
        "2018-absolut.csv",
        "2019-absolut.csv",
        "2020-absolut.csv",
        "2021-absolut.csv",
        "2022-absolut.csv",
        "2023-absolut.csv",
        "2024-absolut.csv",
    ]

    # Load all files and concatenate at once
    # Use Int64 dtype for nullable integers and parse dates for Zeitraum
    monthly_df = pd.concat(
        [
            load_file(
                file,
                dtype={
                    "Besucher": "Int64",
                    "Entleihungen": "Int64",
                    "aktivierte Ausweise": "Int64",
                },
                parse_dates=["Zeitraum"],
                index_col="Zeitraum",
            )
            for file in monthly_files
        ]
    )
    return monthly_df, monthly_files


if __name__ == "__main__":
    app.run()
