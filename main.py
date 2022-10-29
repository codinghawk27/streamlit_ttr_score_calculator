# -*- coding: utf-8 -*-
"""
Created on 22/10/2022.

@author: X

Description: Streamlit app to calculate the resulting TTR-Score after a
tournament.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def main() -> None:
    """Run the streamlit app."""
    initialize_session()
    st.title("TTR-Rechner :table_tennis_paddle_and_ball:")
    sidebar()
    calculator_tab, explanation_tab = st.tabs(["TTR-Rechner", "Erklärung"])
    section_calculator_tab(calculator_tab)
    section_explanation_tab(explanation_tab)


def initialize_session() -> None:
    """Initialize the streamlit session."""
    if "number_of_matches" not in st.session_state:
        st.session_state["number_of_matches"] = 1
    if "change_constant" not in st.session_state:
        st.session_state["change_constant"] = 16
    if "show_grid" not in st.session_state:
        st.session_state["show_grid"] = True
    if "show_graphs" not in st.session_state:
        st.session_state["show_graphs"] = True
    if "use_darkmode" not in st.session_state:
        st.session_state["use_darkmode"] = False
    if "current_ttr_score" not in st.session_state:
        st.session_state["current_ttr_score"] = None
    if "ttr_score_opponent_list" not in st.session_state:
        st.session_state["ttr_score_opponent_list"] = []
    if "result_list" not in st.session_state:
        st.session_state["result_list"] = []
    if "match_results" not in st.session_state:
        st.session_state["match_results"] = 0
    if "new_ttr_score" not in st.session_state:
        st.session_state["new_ttr_score"] = None


def sidebar() -> None:
    """Display the streamlit sidebar."""
    with st.sidebar:
        section_app_settings()
        section_about()


def section_app_settings() -> None:
    """Display and evaluate the app settings options."""
    st.header("Einstellungen :gear:")
    show_graphs = st.checkbox("Zeige Grafiken", value=True)
    st.session_state["show_graphs"] = show_graphs
    show_grid = st.checkbox("Hilfslinien bei Grafiken anzeigen",
                            value=True)
    st.session_state["show_grid"] = show_grid
    use_darkmode = st.checkbox("Darkmode bei Grafiken verwenden",
                               value=False)
    st.session_state["use_darkmode"] = use_darkmode
    st.write("***")


def section_about() -> None:
    """Display the about section."""
    st.header("About :information_source:")
    st.write("Erstellt von codinghawk27")
    st.write("Letzes Update: 29.10.2022")


def section_calculator_tab(
        tab: st.tabs
        ) -> None:
    """
    Display and evaluate the ttr-calculator tab.

    Parameters
    ----------
    tab : st.tabs
        The calculator tab.
    """
    with tab:
        section_current_ttr_points()
        expander_additional_info_for_ttr_calculation()
        section_tournament()
        buttons_add_remove_match()
        section_results()
        expander_detailed_match_summary()


def section_current_ttr_points() -> None:
    """User input section of its' current ttr-points."""
    current_ttr_score = st.number_input("Deine aktuellen TTR-Punkte",
                                        min_value=0,
                                        max_value=3000,
                                        value=1400,
                                        step=1)
    st.session_state["current_ttr_score"] = current_ttr_score


def expander_additional_info_for_ttr_calculation() -> None:
    """User input of additional flags used to calculate the new ttr-score."""
    with st.expander("Weitere Angaben zur Berechnung des TTR-Wertes"):
        no_match_in_365_days = st.checkbox("Kein Einzel in den letzten 365"
                                           " Tagen absolviert (gültig für"
                                           " 15 Einzel)",
                                           value=False)
        less_than_30_total_matches = st.checkbox("Weniger als 30 bewertete"
                                                 " Einzel insgesamt",
                                                 value=False)
        age_under_21 = st.checkbox("Jünger als 21 Jahre", value=False)
        age_under_16 = st.checkbox("Jünger als 16 Jahre", value=False)

        # Calculate the updated change constant
        st.session_state["change_constant"] = \
            calculate_change_constant(
                no_match_in_365_days,
                less_than_30_total_matches,
                age_under_21,
                age_under_16)
        st.write("Änderungskonstante: "
                 f"{st.session_state['change_constant']}")


def calculate_change_constant(
        no_match_in_365_days: bool = False,
        less_than_30_total_matches: bool = False,
        age_under_21:  bool = False,
        age_under_16: bool = False
        ) -> int:
    """
    Calculate the change constant used for the TTR-score calculation.

    The default value is 16, but it increases by 4 with every criterion that
    the user satisfies.

    Parameters
    ----------
    no_match_in_365_days : bool, optional
        Flag, whether no TTR-rated match was played in the last 365 days.
        The default is False.
    less_than_30_total_matches : bool, optional
        Flag, whether the player has less than 30 TTR-rated matches in his
        entire playing career. The default is False.
    age_under_21 : bool, optional
        Flag, whether the player is less than 21 years old.
        The default is False.
    age_under_16 : bool, optional
        Flag, whether the player is less than 16 years old.
        The default is False.

    Returns
    -------
    change_constant : int
        Defines the maximum amount of TTR-points the player can gain /
        lose during each match.
    """
    change_constant = 16

    if no_match_in_365_days:
        change_constant += 4
    if less_than_30_total_matches:
        change_constant += 4
    if age_under_21:
        change_constant += 4
    if age_under_16:
        change_constant += 4

    return change_constant


def section_tournament() -> None:
    """Display the user input section for the tournament."""
    st.session_state["ttr_score_opponent_list"] = []
    st.session_state["result_list"] = []
    st.session_state["match_results"] = 0

    for i in range(st.session_state["number_of_matches"]):
        section_one_match(i)

    new_ttr_score = \
        calculate_new_ttr_score(st.session_state["current_ttr_score"],
                                st.session_state["ttr_score_opponent_list"],
                                st.session_state["match_results"],
                                st.session_state["number_of_matches"])
    st.session_state["new_ttr_score"] = new_ttr_score


def section_one_match(
        match_number: int = 0
        ) -> None:
    """
    User input section for one match of the torunament.

    Parameters
    ----------
    match_number : int, optional
        The match ID in the tournament. The default is 0.
    """
    st.write("***")
    st.subheader(f"Spiel {match_number+1}")
    ttr_score_opponent = st.number_input("TTR-Punkte des Gegners",
                                         min_value=0,
                                         max_value=3000,
                                         value=1400,
                                         step=1,
                                         key=f"number_input_{match_number}")

    victory = st.checkbox("Spiel gewonnen",
                          value=True,
                          key=f"checkbox_{match_number}")

    st.session_state["ttr_score_opponent_list"].append(ttr_score_opponent)
    st.session_state["result_list"].append(victory)
    if victory:
        st.session_state["match_results"] += 1


def calculate_new_ttr_score(
        current_ttr_score: int,
        ttr_score_opponent: list[int],
        result: int = 1,
        number_of_matches: int = 1
        ) -> int:
    """
    Calculate the new TTR-Score based on all singles of a tournament.

    Parameters
    ----------
    current_ttr_score : int
        The current TTR-score of the player.
    ttr_score_opponent : int | list[int]
        The ttr_score(s) of the opponents.
    result : int, optional
        The number of matches won in the tournament. The default is 1.
    number_of_matches : int, optional
        The number of played matches in the tournament. The default is 1.

    Returns
    -------
    new_ttr_score: int
        The new TTR-score of the player after the tournament.
    """
    change_constant = st.session_state["change_constant"]
    expected_result = 0

    # Multiple matches were played
    if isinstance(ttr_score_opponent, list):
        for i in range(number_of_matches):
            winning_propability = calculate_winning_probability(
                ttr_score_player_a=current_ttr_score,
                ttr_score_player_b=ttr_score_opponent[i])
            expected_result += winning_propability
    # Only a single match was played
    else:
        winning_propability = calculate_winning_probability(
            ttr_score_player_a=current_ttr_score,
            ttr_score_player_b=ttr_score_opponent)
        expected_result += winning_propability

    new_ttr_score = current_ttr_score \
        + round((result-expected_result)*change_constant)

    return new_ttr_score


def calculate_winning_probability(
        ttr_score_player_a: int,
        ttr_score_player_b: int
        ) -> float:
    """
    Calculate the winning probability of player A against player b.

    Parameters
    ----------
    ttr_score_player_a : int
        The TTR-score of player A at match-time.
    ttr_score_player_b : int
        The TTR-score of player B at match-time.

    Returns
    -------
    float
        The winning probability of player A for this match.
    """
    exponent = (ttr_score_player_b - ttr_score_player_a) / 150
    return 1 / (1 + pow(10, exponent))


def buttons_add_remove_match() -> None:
    """Buttons to add / remove one match in the tournament."""
    col1, col2 = st.columns([1, 1])
    with col1:
        disabled = st.session_state["number_of_matches"] >= 15
        add_match = st.button("Weiteres Spiel hinzufügen",
                              disabled=disabled)
    with col2:
        disabled = st.session_state["number_of_matches"] == 1
        remove_match = st.button("Letztes Spiel entfernen",
                                 disabled=disabled)

    if add_match:
        if st.session_state["number_of_matches"] < 15:
            st.session_state["number_of_matches"] += 1
        st.experimental_rerun()

    if remove_match:
        if st.session_state["number_of_matches"] > 1:
            st.session_state["number_of_matches"] -= 1
        st.experimental_rerun()
    st.write("***")


def section_results() -> None:
    """Display the new TTR-score of the player."""
    st.header("Ergebnis :clipboard:")
    st.metric("Neuer TTR-Score",
              value=st.session_state["new_ttr_score"],
              delta=st.session_state["new_ttr_score"]
              - st.session_state["current_ttr_score"])


def expander_detailed_match_summary() -> None:
    """Display expander with additional details about the score calculation."""
    with st.expander("Detailierte Ergebnisse anzeigen"):
        for i in range(st.session_state["number_of_matches"]):
            result = 1 if st.session_state["result_list"][i] else 0
            header = "gewonnen :first_place_medal:" if result == 1 \
                else "verloren"
            st.subheader(f"Spiel {i+1} - {header}")
            section_match_ttr_table(i)

            winning_probability = \
                calculate_winning_probability(
                    st.session_state["current_ttr_score"],
                    st.session_state["ttr_score_opponent_list"][i])
            section_winning_probability_bar(winning_probability)

            new_ttr_score = \
                calculate_new_ttr_score(
                    st.session_state["current_ttr_score"],
                    st.session_state["ttr_score_opponent_list"][i],
                    result=result)
            section_new_ttr_score_after_single(new_ttr_score)

            if st.session_state["show_graphs"]:
                section_graphs_after_single(winning_probability,
                                            new_ttr_score,
                                            match_id=i,
                                            result=result)
            st.write("***")


def section_match_ttr_table(
        match_id: int = 0
        ) -> None:
    """
    Display the TTR-difference as table for the given match.

    Parameters
    ----------
    match_id : int, optional
        The ID of the match. The default is 0.
    """
    table = pd.DataFrame({"Dein aktueller TTR-Score":
                         [st.session_state["current_ttr_score"]],
                         "TTR-Wert des Gegners":
                          [st.session_state["ttr_score_opponent_list"]
                           [match_id]],
                          "TTR-Differenz":
                          [st.session_state["ttr_score_opponent_list"]
                           [match_id]
                           - st.session_state["current_ttr_score"]]})

    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                </style>
                """
    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    st.table(table)


def section_winning_probability_bar(
        winning_probability: float
        ) -> None:
    """
    Display a bar of the winning probability for the given match.

    Parameters
    ----------
    winning_probability : float
        The winning probability (between 0 and 1) for the match.
    """
    change_bar_color = """
        <style>
            .stProgress > div > div > div > div {
                background-color: green;
            }
        </style>"""
    st.markdown(change_bar_color, unsafe_allow_html=True)
    st.progress(winning_probability)
    st.write(f"Gewinnerwartung:"
             f" {round(winning_probability, 3)}")


def section_new_ttr_score_after_single(
        new_ttr_score: int
        ) -> None:
    """
    Display the resulting TTR-score, if this would have been the only match.

    Parameters
    ----------
    new_ttr_score : int
        The resulting new TTR-score if only this match was played.
    """
    if st.session_state["number_of_matches"] > 1:
        st.write("Wäre dies das einzige Spiel gewesen, wäre dein"
                 f" neuer TTR-Score: {new_ttr_score}"
                 f" ({new_ttr_score-st.session_state['current_ttr_score']:+}"
                 " Punkte).  \n")
        st.write("Hinweis: Da diese Veranstaltung aus mehreren "
                 " Partien besteht, zählt nur der gesamte "
                 " TTR-Wert. Dieser muss nicht unbedingt der Summe"
                 " der Einzelergebnisse entsprechen."
                 " Weitere Informationen dazu finden sich im"
                 " Reiter \"Erklärung\". ")
    else:
        st.write("Dein neuer TTR-Score ist:"
                 f" {new_ttr_score}"
                 f" ({new_ttr_score-st.session_state['current_ttr_score']:+}"
                 " Punkte).")


def section_graphs_after_single(
        winning_probability: int,
        new_ttr_score: int,
        match_id: int = 0,
        result: int = 1
        ) -> None:
    """
    Display graphs for the given match.

    Parameters
    ----------
    winning_probability : int
        The winning probability for this match.
    new_ttr_score : int
        The new TTR-score, if only this match would have been played.
    match_id : int, optional
        The ID of this match in the tournament. The default is 0.
    result : int, optional
        Indicates, whether this match was won. 1 if match was won,
        0 if match was lost. The default is 1.
    """
    # Set theme
    if st.session_state["use_darkmode"]:
        plt.style.use("dark_background")
    else:
        plt.style.use("default")

    plot_winning_probability(winning_probability,
                             st.session_state["ttr_score_opponent_list"]
                             [match_id]
                             - st.session_state["current_ttr_score"])
    plot_ttr_points_gained(new_ttr_score-st.session_state["current_ttr_score"],
                           st.session_state["ttr_score_opponent_list"]
                           [match_id]
                           - st.session_state["current_ttr_score"],
                           game_won=result)


def plot_winning_probability(
        winning_probability: int = None,
        rating_difference: int = None
        ) -> None:
    """
    Show, where the winning probability is located on a global plot.

    Parameters
    ----------
    winning_probability : int, optional
        The winning probability to highlight in the plot. The default is None.
    rating_difference : int, optional
        The rating difference to highlight in the plot. The default is None.
    """
    rating_differences = define_rating_range(rating_difference)

    # Calculate the winning probability for the entire range of
    # rating differences
    winning_probabilites = []
    for difference in rating_differences:
        probability = calculate_winning_probability(0, difference)
        winning_probabilites.append(round(probability, 3))

    # Create plot
    fig = create_plot_figure(rating_differences, winning_probabilites,
                             xlabel="TTR-Punktedifferenz",
                             ylabel="Gewinnerwartung")
    highlight_point_in_figure(rating_difference, winning_probability)
    st.pyplot(fig)


def define_rating_range(
        rating_difference: int
        ) -> list[int]:
    """
    Define the range of the rating difference, that will later be plotted.

    Parameters
    ----------
    rating_difference : int
        The rating difference.

    Returns
    -------
    rating_differences : list[int]
        A list containing spanning the entire range with step 1.
    """
    if abs(rating_difference) <= 400:
        rating_differences = list(range(-400, 400, 1))
    elif rating_difference > 400:
        rating_differences = list(range(-400, rating_difference, 1))
    else:
        rating_differences = list(range(rating_difference, 400, 1))

    return rating_differences


def create_plot_figure(x_list: list[int],
                       y_list: list[int],
                       xlabel: str,
                       ylabel: str
                       ) -> plt.figure:
    """
    Create a plt.figure of two lists.

    Parameters
    ----------
    x_list : list[int]
        The x-coordinates of all plotted points.
    y_list : list[int]
        The y-coordinates of all plotted points.
    xlabel : str
        The label that will be displayed on the x-axis.
    ylabel : str
        The label that will be displayed on the y-axis..

    Returns
    -------
    fig : plt.figure
        The resulting matplotlib.figure, that can be displayed in streamlit.
    """
    assert len(x_list) == len(y_list), \
        "x and y must contain the same number of entries"

    fig, _ = plt.subplots()
    plt.plot(x_list, y_list, zorder=2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if st.session_state["show_grid"]:
        plt.grid(zorder=1)

    return fig


def highlight_point_in_figure(
        x_coordinate: int,
        y_coordinate: int
        ) -> None:
    """
    Highlight one point in the figure in red.

    Parameters
    ----------
    x_coordinate : int
        The x-coordinate.
    y_coordinate : int
        The y-coordinate.
    """
    plt.scatter(x_coordinate, y_coordinate, color="red", zorder=3)


def plot_ttr_points_gained(
        ttr_points_gained: int = None,
        rating_difference: int = None,
        game_won: bool = True,
        ) -> None:
    """
    Show where the gained ttr-points are located on a global plot.

    Parameters
    ----------
    ttr_points_gained : int, optional
        The ttr-points gained to highlight in the plot. The default is None.
    rating_difference : int, optional
        The rating difference to highlight in the plot. The default is None.
    game_won : bool, optional
        Flag, whether the game was won or lost. This results in the plot
        showing a positive change in TTR-points or a negative change in points.
        The default is True.
    """
    rating_differences = define_rating_range(rating_difference)

    # Calculate the ttr-points gainedfor the entire range of rating differences
    ttr_changes = []
    result = 1 if game_won else 0
    for difference in rating_differences:
        probability = calculate_winning_probability(0, difference)
        change = round((result-probability)
                       * st.session_state["change_constant"])
        ttr_changes.append(change)

    # Create plot
    fig = create_plot_figure(rating_differences, ttr_changes,
                             xlabel="TTR-Punktedifferenz",
                             ylabel="Veränderung TTR-Punkte")
    highlight_point_in_figure(rating_difference, ttr_points_gained)
    st.pyplot(fig)


def section_explanation_tab(
        tab: st.tabs
        ) -> None:
    """
    Display and evaluate the explanation tab.

    Parameters
    ----------
    tab : st.tabs
        The explantion tab.
    """
    with tab:
        section_general_information()
        section_ttr_score_formula()
        section_additional_information()


def section_general_information() -> None:
    """Section showing general information about TTR-points."""
    st.header("Grundsätzliche Informationen :open_book:")
    st.write("TTR steht für Tischtennis-Rating. Der TTR-Wert stellt eine"
             " Metrik für die Spielstärke eines Spielers dar."
             " Für die Berechnung des TTR-Wertes zählen nur Einzel"
             " - keine Doppel. Jedes offizell gewertete Einzel ist dabei"
             " gleich viel wert (unabhängig von der Veranstaltung).")
    st.write("***")


def section_ttr_score_formula() -> None:
    """Section showing the formula used to calculate the TTR-score."""
    st.header("Berechnungsformel :chart_with_upwards_trend:")
    st.write("Der TTR-Score wird mit folgender Formel berechnet:")
    st.latex(r"""
             TTRneu = TTRalt + Rundung\: auf\: ganze\: Zahlen[\{
             (Resultat-erwartetes Resultat)*Änderungskonstante\}]""")
    st.subheader("Resultat")
    st.write("Summe aller Siege des Spielers in einer Veranstaltung."
             " Für jeden Sieg gibt es einen Punkt, für jede Niederlage 0.")
    st.subheader("Erwartetes Resultat")
    st.write("Summe aller Gewinnwahrscheinlichkeiten aller Einzel einer "
             "Veranstaltung. Ist abhängig von der TTR-Differenz der beiden"
             " Spieler. Häufig auch als Gewinnerwartung bezeichnet.")
    st.subheader("Änderungskonstante")
    st.write("Gibt an, wie stark sich der TTR-Score pro Einzel maximal"
             " verändern kann. Der Grundwert ist 16,"
             " das Maximum ist 32.")
    st.write("***")


def section_additional_information() -> None:
    """Section showing a link for further information on the topic."""
    st.header("Weiterführende Informationen :mag:")
    weblink = "https://www.tischtennis.de/fileadmin/documents/" \
              "Satzungen_Ordnungen/2022/20220816-Beschreibung-der" \
              "-andro-Rangliste.pdf"
    st.write("Genauere Informationen zur Berechnung des TTR-Wertes"
             " sind in der offiziellen Beschreibung der  \n"
             " andro-Rangliste von mytischtennis zu finden:")
    st.write(weblink)


if __name__ == "__main__":
    main()
