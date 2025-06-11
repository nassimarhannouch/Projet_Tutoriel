import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
import mysql.connector
from datetime import datetime, timedelta
import os


# Application constants
APP_TITLE = "Dashboard Administrateur - Système d'Analyse des Feedbacks"
FILIERES = ['IID', 'GI', 'MGSI', 'liscense Big Data', 'master Big Data']
DEFAULT_FILIERE = 'IID'

# Database connection function
def connect_to_db():
    """Establish a connection to the MySQL database using environment variables"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "Nassima&&123"),
            database=os.getenv("DB_NAME", "final")
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données: {err}")
        exit(1)

# Function to fetch data from the database for admin dashboard
def get_admin_data():
    """Retrieve data for admin dashboard - Corrigé pour inclure les cours"""
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)
    
    # Requête corrigée pour inclure les informations sur les cours
    query = """
    SELECT 
        u.id, 
        u.username,
        u.first_name,
        u.last_name,
        u.email, 
        u.role, 
        f.nom AS filiere,
        p.nom AS promotion_nom,
        p.annee_debut AS promo_annee,
        c.nom AS cours,
        COUNT(fb.id) AS feedback_count,
        SUM(CASE WHEN fb.sentiment = 'négatif' THEN 1 ELSE 0 END) AS negative_feedback,
        SUM(CASE WHEN fb.sentiment = 'positif' THEN 1 ELSE 0 END) AS positive_feedback,
        AVG(fb.note) AS note_moyenne
    FROM 
        appcours_utilisateur u
    LEFT JOIN 
        appcours_filiere f ON u.filiere_id = f.id
    LEFT JOIN 
        appcours_promotion p ON u.promotion_id = p.id
    LEFT JOIN 
        appcours_feedback fb ON u.id = fb.etudiant_id
    LEFT JOIN 
        appcours_cours c ON fb.cours_id = c.id
    GROUP BY 
        u.id, f.nom, p.nom, p.annee_debut, c.nom
    """
    
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        
        if df.empty:
            df = pd.DataFrame(columns=[
                'id', 'username', 'first_name', 'last_name', 'email', 'role', 'filiere', 
                'promotion_nom', 'promo_annee', 'cours', 'feedback_count', 'negative_feedback', 
                'positive_feedback', 'note_moyenne'
            ])
        else:
            # Créer le nom complet
            df['nom'] = df.apply(lambda row: f"{row['first_name']} {row['last_name']}" if row['first_name'] and row['last_name'] else row['username'], axis=1)
            # Utiliser promo_annee comme promo pour la compatibilité
            df['promo'] = df['promo_annee']
            
            # Remplacer les valeurs None par des valeurs par défaut
            df['feedback_count'] = df['feedback_count'].fillna(0)
            df['negative_feedback'] = df['negative_feedback'].fillna(0)
            df['positive_feedback'] = df['positive_feedback'].fillna(0)
            df['note_moyenne'] = df['note_moyenne'].fillna(0)
            df['cours'] = df['cours'].fillna('Cours non spécifié')
        
        return df
    except mysql.connector.Error as err:
        print(f"Erreur lors de la récupération des données admin: {err}")
        return pd.DataFrame()
    finally:
        cursor.close()
        connection.close()

# Fonction alternative pour récupérer uniquement les données des cours par filière
def get_courses_data_by_filiere(selected_filiere=None):
    """Récupère les données spécifiques aux cours pour une filière donnée"""
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)
    
    # Requête optimisée pour les cours
    query = """
    SELECT 
        c.nom AS cours,
        f.nom AS filiere,
        COUNT(fb.id) AS feedback_count,
        SUM(CASE WHEN fb.sentiment = 'négatif' THEN 1 ELSE 0 END) AS negative_feedback,
        SUM(CASE WHEN fb.sentiment = 'positif' THEN 1 ELSE 0 END) AS positive_feedback,
        AVG(fb.note) AS note_moyenne,
        COUNT(DISTINCT fb.etudiant_id) AS nombre_etudiants
    FROM 
        appcours_cours c
    LEFT JOIN 
        appcours_feedback fb ON c.id = fb.cours_id
    LEFT JOIN 
        appcours_utilisateur u ON fb.etudiant_id = u.id
    LEFT JOIN 
        appcours_filiere f ON u.filiere_id = f.id
    WHERE 
        c.nom IS NOT NULL 
        AND (f.nom = %s OR %s IS NULL)
    GROUP BY 
        c.nom, f.nom
    HAVING 
        feedback_count > 0
    ORDER BY 
        feedback_count DESC
    """
    
    try:
        cursor.execute(query, (selected_filiere, selected_filiere))
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        
        if not df.empty:
            # Remplacer les valeurs None par des valeurs par défaut
            df['feedback_count'] = df['feedback_count'].fillna(0)
            df['negative_feedback'] = df['negative_feedback'].fillna(0)
            df['positive_feedback'] = df['positive_feedback'].fillna(0)
            df['note_moyenne'] = df['note_moyenne'].fillna(0)
            df['nombre_etudiants'] = df['nombre_etudiants'].fillna(0)
            
        return df
    except mysql.connector.Error as err:
        print(f"Erreur lors de la récupération des données cours: {err}")
        return pd.DataFrame()
    finally:
        cursor.close()
        connection.close()

def get_admin_data_debug():
    """Version de débogage pour identifier les problèmes"""
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # D'abord, vérifier les utilisateurs
        cursor.execute("SELECT * FROM appcours_utilisateur LIMIT 5")
        users = cursor.fetchall()
        print("Utilisateurs trouvés:", len(users))
        
        # Vérifier les filières
        cursor.execute("SELECT * FROM appcours_filiere")
        filieres = cursor.fetchall()
        print("Filières trouvées:", len(filieres))
        
        # Vérifier les cours
        cursor.execute("SELECT * FROM appcours_cours LIMIT 5")
        cours = cursor.fetchall()
        print("Cours trouvés:", len(cours))
        
        # Vérifier les feedbacks
        cursor.execute("SELECT * FROM appcours_feedback LIMIT 5")
        feedbacks = cursor.fetchall()
        print("Feedbacks trouvés:", len(feedbacks))
        
        # Requête simplifiée pour commencer
        simple_query = """
        SELECT 
            u.id, 
            u.username,
            u.first_name,
            u.last_name,
            u.email, 
            u.role, 
            f.nom AS filiere,
            c.nom AS cours
        FROM 
            appcours_utilisateur u
        LEFT JOIN 
            appcours_filiere f ON u.filiere_id = f.id
        LEFT JOIN 
            appcours_feedback fb ON u.id = fb.etudiant_id
        LEFT JOIN 
            appcours_cours c ON fb.cours_id = c.id
        """
        
        cursor.execute(simple_query)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        
        if not df.empty:
            df['nom'] = df.apply(lambda row: f"{row['first_name']} {row['last_name']}" if row['first_name'] and row['last_name'] else row['username'], axis=1)
            # Ajouter des colonnes par défaut pour éviter les erreurs
            df['feedback_count'] = 0
            df['negative_feedback'] = 0
            df['positive_feedback'] = 0
            df['note_moyenne'] = 0
            df['promo'] = 2024  # Valeur par défaut
            df['cours'] = df['cours'].fillna('Aucun cours')
            df['promotion_nom'] = 'Aucune promotion'
            df['promo_annee'] = 2024
        
        return df
        
    except mysql.connector.Error as err:
        print(f"Erreur lors du débogage: {err}")
        return pd.DataFrame()
    finally:
        cursor.close()
        connection.close()

# Alternative: Fonction pour récupérer les données via Django ORM (si vous utilisez Django)
def get_admin_data_django():
    """Alternative utilisant Django ORM - à utiliser si vous intégrez dans Django"""
    try:
        from django.db.models import Count, Avg, Case, When, IntegerField
        from appcours.models import Utilisateur, Feedback  # Remplacez par vos vrais imports
        
        # Récupérer les données avec les relations
        users_data = Utilisateur.objects.select_related('filiere', 'promotion').prefetch_related('feedbacks').annotate(
            feedback_count=Count('feedbacks'),
            positive_feedback=Count(
                Case(When(feedbacks__sentiment='positif', then=1), output_field=IntegerField())
            ),
            negative_feedback=Count(
                Case(When(feedbacks__sentiment='négatif', then=1), output_field=IntegerField())
            ),
            note_moyenne=Avg('feedbacks__note')
        )
        
        data = []
        for user in users_data:
            for feedback in user.feedbacks.all():
                data.append({
                    'id': user.id,
                    'username': user.username,
                    'nom': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                    'email': user.email,
                    'role': user.role,
                    'filiere': user.filiere.nom if user.filiere else None,
                    'promo': user.promotion.annee_debut if user.promotion else None,
                    'promotion_nom': user.promotion.nom if user.promotion else None,
                    'feedback_count': user.feedback_count,
                    'positive_feedback': user.positive_feedback,
                    'negative_feedback': user.negative_feedback,
                    'cours': feedback.cours.nom if feedback.cours else None,
                    'note_moyenne': user.note_moyenne
                })
        
        return pd.DataFrame(data)
    except ImportError:
        print("Django non disponible, utilisation de la requête SQL directe")
        return get_admin_data()

# Initialize Dash application
external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = APP_TITLE

colors = {
    'background': '#f8f9fa',
    'card': '#ffffff',
    'text': '#333333',
    'primary': '#6E67FF',
    'secondary': "#C400F5",
    'success': "#EB67FF",
    'subtext': '#718096',
    'warning': '#6E67FF',
    'info': '#10B981',
    'positive': "#6A63EAD6",
    'negative': '#FC67FA',
}

app.layout = html.Div([
    # Header avec nouveau design
    html.Div(
        style={
            'display': 'flex', 
            'justifyContent': 'space-between', 
            'alignItems': 'center',
            'backgroundColor': colors['card'],  # Utilise la couleur de carte au lieu d'un fond coloré
            'padding': '20px 25px', 
            'borderRadius': '12px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 
            'marginBottom': '25px',
            'border': f'1px solid {colors.get("border", "#e0e0e0")}'  # Bordure subtile
        }, 
        children=[
            # Section gauche avec icône et texte
            html.Div(
                style={
                    'display': 'flex', 
                    'alignItems': 'center'
                }, 
                children=[
                    html.I(
                        style={
                            'fontSize': '28px', 
                            'color': colors['primary'], 
                            'marginRight': '15px'
                        }
                    ),
                    html.Div([
                        html.H1(
                            "Dashboard Administrateur", 
                            style={
                                'margin': '0', 
                                'color': colors['primary'], 
                                'fontSize': '28px',
                                'fontWeight': '600'
                            }
                        ),
                        html.P(
                            "Vue d'ensemble du système d'analyse des feedbacks étudiants",
                            style={
                                'margin': '5px 0 0 0', 
                                'color': '#666', 
                                'fontSize': '16px',
                                'fontWeight': '400'
                            }
                        )
                    ])
                ]
            )
    ]),
    
    # Filters section avec le même style que le header
html.Div(
    style={
        'display': 'flex', 
        'justifyContent': 'space-between', 
        'alignItems': 'center',
        'backgroundColor': colors['card'],
        'padding': '20px 25px', 
        'borderRadius': '12px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 
        'marginBottom': '25px',
        'border': f'1px solid {colors.get("border", "#e0e0e0")}'
    }, 
    children=[
        # Section gauche avec le filtre
        html.Div(
            style={
                'display': 'flex', 
                'alignItems': 'center'
            }, 
            children=[
                html.I(
                    className="fas fa-filter",  # Icône de filtre
                    style={
                        'fontSize': '24px', 
                        'color': colors['primary'], 
                        'marginRight': '15px'
                    }
                ),
                html.Div([
                    html.Label(
                        "Sélectionner une filière:",
                        style={
                            'margin': '0', 
                            'color': colors['primary'], 
                            'fontSize': '18px',
                            'fontWeight': '600',
                            'marginBottom': '5px',
                            'display': 'block'
                        }
                    ),
                    dcc.Dropdown(
                        id='filiere-dropdown',
                        options=[{'label': filiere, 'value': filiere} for filiere in FILIERES],
                        value=DEFAULT_FILIERE,
                        clearable=False,
                        style={
                            'width': '250px',
                            'fontSize': '14px'
                        }
                    )
                ])
            ]
        ),
        
        # Section droite (optionnelle) - peut contenir d'autres filtres ou actions
        html.Div(
            style={
                'display': 'flex', 
                'alignItems': 'center', 
                'gap': '15px'
            },
            children=[
                html.Div(
                    style={
                        'padding': '8px 16px',
                        'backgroundColor': colors.get('background', '#f8f9fa'),
                        'borderRadius': '6px',
                        'fontSize': '14px',
                        'color': colors.get('subtext', '#666'),
                        'border': f'1px solid {colors.get("border", "#e0e0e0")}'
                    },
                    children="Filtres actifs"
                )
            ]
        )
    ]
),
    
    # KPIs row
    html.Div([
        html.Div([
            html.H4("Total Étudiants", className="kpi-title"),
            html.H2(id="total-students", className="kpi-value"),
            html.Span("Actifs", className="kpi-change")
        ], className="kpi-card"),
        
        html.Div([
            html.H4("Total Feedbacks", className="kpi-title"),
            html.H2(id="total-feedbacks", className="kpi-value"),
            html.Span("Cette année", className="kpi-change")
        ], className="kpi-card"),
        
        html.Div([
            html.H4("Note Moyenne", className="kpi-title"),
            html.H2(id="average-note", className="kpi-value"),
            html.Span("Sur 5", className="kpi-change")
        ], className="kpi-card"),
        
        html.Div([
            html.H4("Taux Satisfaction", className="kpi-title"),
            html.H2(id="satisfaction-rate", className="kpi-value"),
            html.Span("Feedbacks positifs", className="kpi-change")
        ], className="kpi-card"),
    ], className="kpi-row"),
    
    # Charts row 1
    html.Div([
        html.Div([
            html.H3("Distribution des Feedbacks par Sentiment", className="chart-title"),
            dcc.Graph(id='feedback-sentiment-chart')
        ], className="chart-card"),
        
        html.Div([
            html.H3("Répartition des Étudiants par Promotion", className="chart-title"),
            dcc.Graph(id='student-promo-chart')
        ], className="chart-card")
    ], className="charts-row"),
    
    # Charts row 2
    html.Div([
        html.Div([
            html.H3("Top 10 Cours par Nombre de Feedbacks", className="chart-title"),
            dcc.Graph(id='top-courses-chart')
        ], className="chart-card full-width")
    ], className="charts-row"),
    
    # Charts row 3
    html.Div([
        html.Div([
            html.H3("Comparaison des Filières", className="chart-title"),
            dcc.Graph(id='filiere-comparison-chart')
        ], className="chart-card"),
        
        html.Div([
            html.H3("Évolution des Notes Moyennes", className="chart-title"),
            dcc.Graph(id='notes-evolution-chart')
        ], className="chart-card")
    ], className="charts-row"),
    
    # Bottom section
    html.Div([
        html.Div([
            html.H3("Liste des Chefs de Filière", className="chart-title"),
            html.Div(id='chef-list')
        ], className="chart-card"),
        
        html.Div([
            html.H3("Statistiques Détaillées", className="chart-title"),
            html.Div(id='detailed-stats')
        ], className="chart-card")
    ], className="charts-row")
], className="app-container")

# Callbacks for KPIs
@app.callback(
    [Output('total-students', 'children'),
     Output('total-feedbacks', 'children'),
     Output('average-note', 'children'),
     Output('satisfaction-rate', 'children')],
    Input('filiere-dropdown', 'value')
)
def update_kpis(selected_filiere):
    df = get_admin_data()
    if df.empty:
        return "0", "0", "0.0", "0%"
    
    filtered_data = df[df['filiere'] == selected_filiere]
    
    total_students = len(filtered_data['id'].unique()) if not filtered_data.empty else 0
    total_feedbacks = filtered_data['feedback_count'].sum() if not filtered_data.empty else 0
    avg_note = filtered_data['note_moyenne'].mean() if not filtered_data.empty and not filtered_data['note_moyenne'].isna().all() else 0
    
    positive_feedbacks = filtered_data['positive_feedback'].sum() if not filtered_data.empty else 0
    satisfaction_rate = (positive_feedbacks / max(total_feedbacks, 1)) * 100
    
    return f"{total_students}", f"{total_feedbacks}", f"{avg_note:.1f}/5", f"{satisfaction_rate:.1f}%"

# Callback for feedback sentiment chart
@app.callback(
    Output('feedback-sentiment-chart', 'figure'),
    Input('filiere-dropdown', 'value')
)
def update_feedback_sentiment_chart(selected_filiere):
    df = get_admin_data()
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    filtered_data = df[df['filiere'] == selected_filiere]
    
    if filtered_data.empty:
        positive_count = 0
        negative_count = 0
    else:
        positive_count = filtered_data['positive_feedback'].sum()
        negative_count = filtered_data['negative_feedback'].sum()
    
    sentiment_data = pd.DataFrame({
        'Sentiment': ['Positif', 'Négatif'],
        'Nombre': [positive_count, negative_count]
    })
    
    fig = px.bar(
        sentiment_data,
        x='Sentiment',
        y='Nombre',
        color='Sentiment',
        color_discrete_map={'Positif': '#C8A8E9', 'Négatif': '#E3AADD'}
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=40),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

@app.callback(
    Output('student-promo-chart', 'figure'),
    Input('filiere-dropdown', 'value')
)
def update_student_promo_chart(selected_filiere):
    df = get_admin_data()
    
    # Debug: Afficher les données récupérées
    print("DataFrame shape:", df.shape)
    print("Colonnes disponibles:", df.columns.tolist())
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible dans la base",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    if not df.empty:
        print("Premières lignes:")
        print(df.head())
        # Vérification des colonnes liées aux promotions selon votre modèle
        promotion_columns = ['promotion_nom', 'promotion_id', 'promotion__nom']
        for col in promotion_columns:
            if col in df.columns:
                print(f"Valeurs uniques de '{col}':", df[col].unique())
    
    # Filtrer les données par filière
    if selected_filiere and selected_filiere != 'all':
        # Essayer différents noms de colonnes pour la filière
        filiere_columns = ['filiere', 'filiere_nom', 'filiere__nom']
        filiere_column = None
        
        for col in filiere_columns:
            if col in df.columns:
                filiere_column = col
                break
        
        if filiere_column:
            filtered_data = df[df[filiere_column] == selected_filiere]
        else:
            print("Aucune colonne de filière trouvée")
            filtered_data = df
    else:
        filtered_data = df
    
    print(f"Données filtrées pour {selected_filiere}:", filtered_data.shape)
    
    if filtered_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Aucune donnée pour la filière {selected_filiere}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    # Identifier la colonne promotion selon votre modèle Django
    promo_column = None
    possible_promo_columns = [
        'promotion__nom',  # Si vous utilisez select_related
        'promotion_nom',   # Si vous renommez la colonne
        'promotion_id',    # Si vous voulez utiliser l'ID
        'promo',          # Nom générique
        'promo_annee'     # Si vous calculez l'année
    ]
    
    for col in possible_promo_columns:
        if col in filtered_data.columns and not filtered_data[col].isna().all():
            promo_column = col
            break
    
    # Si aucune colonne promotion n'est trouvée, créer des données basées sur le modèle
    if promo_column is None:
        print("Aucune colonne promotion trouvée, vérification des données utilisateur")
        
        # Filtrer uniquement les étudiants (selon votre modèle Utilisateur)
        if 'role' in filtered_data.columns:
            student_data = filtered_data[filtered_data['role'] == 'etudiant']
        else:
            student_data = filtered_data
        
        if student_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucun étudiant trouvé dans cette filière",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            return fig
        
        # Créer des promotions par défaut si aucune n'existe
        print("Création de données de promotion par défaut")
        student_data = student_data.copy()
        
        # Assigner des promotions basées sur l'année d'inscription ou ID
        if 'date_joined' in student_data.columns:
            student_data['promotion_calculee'] = student_data['date_joined'].dt.year.apply(
                lambda x: f"Promotion {x}"
            )
        else:
            # Fallback: utiliser l'ID pour créer des promotions
            student_data['promotion_calculee'] = student_data.apply(
                lambda row: f"Promotion {2020 + (row.get('id', 0) % 5)}", axis=1
            )
        
        promo_column = 'promotion_calculee'
        filtered_data = student_data
    
    print(f"Utilisation de la colonne: {promo_column}")
    
    # Compter les étudiants par promotion
    promo_counts = filtered_data[promo_column].value_counts()
    print("Comptage des promotions:", promo_counts.to_dict())
    
    if promo_counts.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée de promotion disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    # Créer le graphique en secteurs
    fig = px.pie(
        values=promo_counts.values,
        names=promo_counts.index,
        title=f"Répartition des étudiants par promotion - {selected_filiere}",
        color_discrete_sequence=['#C8A8E9', '#F6BCBA', '#E3AADD', '#F2DDDC', '#C3C7F4']
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Nombre d\'étudiants: %{value}<br>Pourcentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,
        font=dict(size=12)
    )
    
    return fig

# Callback for filiere comparison chart
@app.callback(
    Output('filiere-comparison-chart', 'figure'),
    Input('filiere-dropdown', 'value')
)
def update_filiere_comparison_chart(selected_filiere):
    df = get_admin_data()
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    filiere_stats = df.groupby('filiere').agg({
        'feedback_count': 'sum',
        'positive_feedback': 'sum',
        'negative_feedback': 'sum'
    }).reset_index()
    
    fig = px.bar(
        filiere_stats,
        x='filiere',
        y=['positive_feedback', 'negative_feedback'],
        color_discrete_map={'positive_feedback': '#C8A8E9', 'negative_feedback': '#E3AADD'},
        barmode='stack'
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=40),
        legend_title_text='Type de Feedback'
    )
    
    newnames = {'positive_feedback': 'Positif', 'negative_feedback': 'Négatif'}
    fig.for_each_trace(lambda t: t.update(name=newnames[t.name]))
    
    return fig

# Callback for notes evolution chart
@app.callback(
    Output('notes-evolution-chart', 'figure'),
    Input('filiere-dropdown', 'value')
)
def update_notes_evolution_chart(selected_filiere):
    df = get_admin_data()
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    filtered_data = df[df['filiere'] == selected_filiere]
    
    if filtered_data.empty or filtered_data['note_moyenne'].isna().all():
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée de notes disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Évolution temporelle par promotion
    promo_notes = filtered_data.groupby('promo')['note_moyenne'].mean().reset_index()
    promo_notes = promo_notes.dropna()
    
    if promo_notes.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée de notes par promotion disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    fig = px.line(
        promo_notes,
        x='promo',
        y='note_moyenne',
        markers=True,
        line_shape='spline'
    )
    
    fig.update_traces(line_color='#C8A8E9', marker_color='#E3AADD')
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis_title="Promotion",
        yaxis_title="Note Moyenne"
    )
    
    return fig

# Callback for chef list - Adapté pour Django
@app.callback(
    Output('chef-list', 'children'),
    Input('filiere-dropdown', 'value')
)
def update_chef_list(selected_filiere):
    df = get_admin_data()
    if df.empty:
        return html.Div("Aucune donnée disponible", className="no-data-message")
    
    # Recherche des chefs de filière selon le modèle Django
    chefs = df[(df['filiere'] == selected_filiere) & (df['role'] == 'chef_filiere')]
    
    if chefs.empty:
        return html.Div("Aucun chef de filière trouvé pour cette filière", className="no-data-message")
    
    chef_list = []
    for _, chef in chefs.iterrows():
        chef_list.append(
            html.Div([
                html.Div([
                    html.I(className="fas fa-user", style={'marginRight': '10px', 'color': '#C8A8E9'}),
                    html.Strong(f"{chef['nom']}", style={'color': '#333'}),
                ], style={'marginBottom': '5px'}),
                html.Div([
                    html.I(className="fas fa-envelope", style={'marginRight': '10px', 'color': '#F6BCBA'}),
                    html.Span(f"{chef['email']}", style={'color': '#666'})
                ], style={'marginBottom': '5px'}),
                html.Div([
                    html.I(className="fas fa-graduation-cap", style={'marginRight': '10px', 'color': '#E3AADD'}),
                    html.Span(f"Filière: {chef['filiere']}", style={'color': '#666'})
                ])
            ], className="chef-item")
        )
    
    return chef_list

# Mappage des colonnes selon vos données réelles
COLUMN_MAPPING = {
    'filiere': 'filiere',
    'promo': 'promotion_nom',  # Votre vraie colonne promotion
    'feedback_count': 'feedback_count'
    # Pas de colonne cours car elle n'existe pas dans vos données utilisateurs
}

# Callback pour les statistiques détaillées
@app.callback(
    Output('detailed-stats', 'children'),
    Input('filiere-dropdown', 'value')
)
def update_detailed_stats(selected_filiere):
    try:
        df = get_admin_data()
        
        if df is None or df.empty:
            return html.Div("Aucune donnée disponible", className="no-data-message")
        
        # Vérifier si la colonne filière existe
        filiere_col = COLUMN_MAPPING['filiere']
        if filiere_col not in df.columns:
            available_cols = df.columns.tolist()
            return html.Div(f"Colonne '{filiere_col}' manquante. Colonnes disponibles: {available_cols}", className="no-data-message")
        
        if selected_filiere is None:
            return html.Div("Veuillez sélectionner une filière", className="no-data-message")
        
        filtered_data = df[df[filiere_col] == selected_filiere]
        
        if filtered_data.empty:
            return html.Div("Aucune donnée pour cette filière", className="no-data-message")
        
        # Calculs adaptés à vos données
        total_students = len(filtered_data)  # Nombre d'étudiants
        total_promos = 0
        avg_feedback_per_student = 0
        total_feedbacks = 0
        
        promo_col = COLUMN_MAPPING['promo']
        feedback_col = COLUMN_MAPPING['feedback_count']
        
        if promo_col in filtered_data.columns:
            total_promos = len(filtered_data.dropna(subset=[promo_col])[promo_col].unique())
        
        if feedback_col in filtered_data.columns:
            avg_feedback_per_student = filtered_data[feedback_col].mean() if not filtered_data[feedback_col].isna().all() else 0
            total_feedbacks = filtered_data[feedback_col].sum()
        
        stats = [
            html.Div([
                html.Strong("Nombre d'étudiants: "),
                html.Span(f"{total_students}", style={'color': '#C8A8E9', 'fontWeight': 'bold'})
            ], className="stat-item"),
            html.Div([
                html.Strong("Nombre de promotions: "),
                html.Span(f"{total_promos}", style={'color': '#F6BCBA', 'fontWeight': 'bold'})
            ], className="stat-item"),
            html.Div([
                html.Strong("Total feedbacks: "),
                html.Span(f"{total_feedbacks}", style={'color': '#E3AADD', 'fontWeight': 'bold'})
            ], className="stat-item"),
            html.Div([
                html.Strong("Moyenne feedbacks/étudiant: "),
                html.Span(f"{avg_feedback_per_student:.1f}", style={'color': '#C3C7F4', 'fontWeight': 'bold'})
            ], className="stat-item")
        ]
        
        return stats
        
    except Exception as e:
        return html.Div(f"Erreur: {str(e)}", className="error-message")

# Fonction alternative pour déboguer - récupère d'abord les utilisateurs


# Callback for top courses chart - VERSION AVEC DESIGN AMÉLIORÉ
@app.callback(
    Output('top-courses-chart', 'figure'),
    Input('filiere-dropdown', 'value')
)
def update_top_courses_chart(selected_filiere):
    try:
        df = get_admin_data()
        
        def create_empty_figure(message):
            fig = go.Figure()
            fig.add_annotation(
                text=message,
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            return fig
        
        if df.empty:
            return create_empty_figure("Aucune donnée disponible")
        
        if selected_filiere is None:
            return create_empty_figure("Veuillez sélectionner une filière")
        
        filtered_data = df[df['filiere'] == selected_filiere]
        
        if filtered_data.empty:
            return create_empty_figure("Aucune donnée pour cette filière")
        
        filtered_data_clean = filtered_data.dropna(subset=['cours']).copy()

        # Nettoyer les espaces et convertir en minuscule pour la comparaison
        filtered_data_clean['cours'] = filtered_data_clean['cours'].str.strip()

        # Liste étendue des valeurs à exclure (plus complète)
        valeurs_a_exclure = [
            'non spécifié', 'non specifie', 'cours non spécifié', 'cours non specifie',
            'non spécifie', 'non specifié', 'non défini', 'non defini',
            '', 'n/a', 'na', 'null', 'none', 'aucun', 'non renseigné', 'non renseigne',
            'non applicable', 'non mentionné', 'non mentionne', 'indéterminé', 'indetermine'
        ]

        # Filtrer les cours non pertinents avec une comparaison plus robuste
        mask = ~filtered_data_clean['cours'].str.lower().str.strip().isin(valeurs_a_exclure)
        filtered_data_clean = filtered_data_clean[mask]
        
        # Convertir les colonnes numériques
        numeric_columns = ['feedback_count', 'negative_feedback', 'positive_feedback']
        for col in numeric_columns:
            if col in filtered_data_clean.columns:
                filtered_data_clean[col] = pd.to_numeric(filtered_data_clean[col], errors='coerce').fillna(0)
        
        # Grouper par cours et calculer les métriques
        cours_stats = filtered_data_clean.groupby('cours').agg({
            'feedback_count': 'sum',
            'positive_feedback': 'sum',
            'negative_feedback': 'sum'
        }).reset_index()
        
        if cours_stats.empty:
            return create_empty_figure("Aucune donnée de feedback disponible")
        
        # Convertir en float pour éviter les erreurs de type
        cours_stats['feedback_count'] = cours_stats['feedback_count'].astype(float)
        cours_stats['positive_feedback'] = cours_stats['positive_feedback'].astype(float)
        cours_stats['negative_feedback'] = cours_stats['negative_feedback'].astype(float)
        
        # Calculer le taux de satisfaction
        cours_stats['total_sentiment_feedbacks'] = (
            cours_stats['positive_feedback'] + cours_stats['negative_feedback']
        )
        
        def calculate_satisfaction(row):
            if row['total_sentiment_feedbacks'] > 0:
                return float(row['positive_feedback'] / row['total_sentiment_feedbacks'] * 100)
            else:
                return 50.0  # Valeur par défaut
        
        cours_stats['satisfaction_ratio'] = cours_stats.apply(calculate_satisfaction, axis=1)
        
        # Calculer une note globale combinant satisfaction et nombre de feedbacks
        max_feedbacks = float(cours_stats['feedback_count'].max())
        if max_feedbacks > 0:
            cours_stats['feedback_score'] = (
                cours_stats['feedback_count'] / max_feedbacks * 100.0
            ).astype(float)
        else:
            cours_stats['feedback_score'] = 0.0
            
        cours_stats['score_global'] = (
            cours_stats['satisfaction_ratio'] * 0.6 + 
            cours_stats['feedback_score'] * 0.4
        ).astype(float)
        
        # Trier par score global et prendre le top 10
        top_cours = cours_stats.nlargest(10, 'score_global')
        
        # Créer le graphique avec couleur uniforme
        fig = px.bar(
            top_cours,
            x='score_global',
            y='cours',
            orientation='h',
            title=f"Top 10 des cours - {selected_filiere}",
            labels={
                'score_global': 'Score Global',
                'cours': 'Cours'
            }
        )
        
        # Appliquer la couleur uniforme #C8A8E9
        fig.update_traces(marker_color='#C8A8E9')
        
        # Personnaliser les tooltips
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>" +
                         "Score global: %{x:.1f}<br>" +
                         "Taux de satisfaction: %{customdata[3]:.1f}%<br>" +
                         "Total feedbacks: %{customdata[0]}<br>" +
                         "Feedbacks positifs: %{customdata[1]}<br>" +
                         "Feedbacks négatifs: %{customdata[2]}<br>" +
                         "<extra></extra>",
            customdata=top_cours[['feedback_count', 'positive_feedback', 'negative_feedback', 'satisfaction_ratio']].values,
            marker_color='#C8A8E9'
        )
        
        # Configuration du graphique avec couleur uniforme
        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=40),
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_font=dict(size=16, color='#333'),
            yaxis_title_font=dict(size=14),
            xaxis_title_font=dict(size=14),
            xaxis_title="Score Global",
            yaxis_title="Cours"
        )
        
        # Ajuster la largeur des barres si peu de données
        if len(top_cours) < 5:
            fig.update_traces(width=0.6)
        
        return fig
    
    except Exception as e:
        print(f"Erreur dans update_top_courses_chart: {str(e)}")
        import traceback
        traceback.print_exc()
        
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur lors du chargement des données: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig
# CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }
            
            .app-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .main-header {
                background: linear-gradient(135deg, #C8A8E9 0%, #E3AADD 50%, #F6BCBA 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            
            .filters-section {
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .kpi-row {
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .kpi-card {
                flex: 1;
                background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 4px solid #C8A8E9;
            }
            
            .kpi-title {
                margin: 0 0 15px 0;
                font-size: 14px;
                color: #666;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .kpi-value {
                margin: 15px 0;
                font-size: 28px;
                font-weight: bold;
                color: #333;
            }
            
            .kpi-change {
                font-size: 12px;
                color: #C8A8E9;
                font-weight: 500;
            }
            
            .charts-row {
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .chart-card {
                flex: 1;
                background-color: #fff;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .chart-card.full-width {
                flex: 1;
                width: 100%;
            }
            
            .chart-title {
                margin: 0 0 20px 0;
                color: #333;
                font-size: 18px;
                font-weight: 600;
                border-bottom: 2px solid #C8A8E9;
                padding-bottom: 10px;
            }
            
            .chef-item {
                padding: 15px;
                margin-bottom: 15px;
                background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
                border-radius: 10px;
                border-left: 4px solid #C8A8E9;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            .stat-item {
                padding: 10px 0;
                border-bottom: 1px solid #f0f0f0;
                font-size: 16px;
            }
            
            .no-data-message {
                padding: 20px;
                color: #666;
                font-style: italic;
                text-align: center;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .kpi-row, .charts-row {
                    flex-direction: column;
                }
                
                .chart-card {
                    margin-bottom: 20px;
                }
                
                .app-container {
                    padding: 10px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
from flask_cors import CORS
CORS(app.server)  # Ajoute cette ligne

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

