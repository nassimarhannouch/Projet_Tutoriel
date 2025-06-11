import mysql.connector
import pandas as pd
import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime, timedelta

# Connexion à MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Nassima&&123",
    database="final"
)

# Créer un curseur
cursor = db_connection.cursor()

# Récupérer données de l'utilisateur avec rôle chef de filière
cursor.execute("""
    SELECT 
        first_name, 
        last_name, 
        email,
        filiere_id
    FROM appcours_utilisateur 
    WHERE role = 'chef_filiere' 
    LIMIT 1
""")
user_data = cursor.fetchone()

user_name = f"{user_data[0]} {user_data[1]}" if user_data else "Chef de filière"
user_email = user_data[2] if user_data else "chefdefiliere@exemple.com"
user_filiere_id = user_data[3] if user_data else None

# Si c'est un chef de filière, récupérer seulement les données de sa filière
if user_filiere_id:
    # 1. Récupérer les cours de la filière du chef connecté
    cursor.execute("""
        SELECT c.id, c.nom, f.nom as filiere_nom 
        FROM appcours_cours c
        LEFT JOIN appcours_filiere f ON c.filiere_id = f.id
        WHERE c.filiere_id = %s
    """, (user_filiere_id,))
    cours_data = cursor.fetchall()
    
    # 2. Récupérer les feedbacks pour la filière du chef connecté
    cursor.execute("""
        SELECT 
            f.id,
            f.commentaire,
            f.note,
            f.cours_id,
            f.professeur_id,
            f.etudiant_id,
            f.date_creation,
            f.sentiment,
            f.suggestions,
            f.anonyme,
            f.partager,
            c.nom as cours_nom,
            fi.nom as filiere_nom,
            p.nom as prof_nom,
            p.prenom as prof_prenom,
            u.first_name as etudiant_prenom,
            u.last_name as etudiant_nom
        FROM appcours_feedback f
        LEFT JOIN appcours_cours c ON f.cours_id = c.id
        LEFT JOIN appcours_filiere fi ON c.filiere_id = fi.id
        LEFT JOIN appcours_professeur p ON f.professeur_id = p.id
        LEFT JOIN appcours_utilisateur u ON f.etudiant_id = u.id
        WHERE c.filiere_id = %s
    """, (user_filiere_id,))
    feedback_data = cursor.fetchall()
    
    # 3. Récupérer les professeurs qui enseignent dans la filière du chef
    cursor.execute("""
        SELECT DISTINCT p.id, p.nom, p.prenom, p.email,
               COUNT(DISTINCT pc.cours_id) as nb_cours,
               AVG(f.note) as note_moyenne
        FROM appcours_professeur p
        LEFT JOIN appcours_professeur_cours pc ON p.id = pc.professeur_id
        LEFT JOIN appcours_cours c ON pc.cours_id = c.id
        LEFT JOIN appcours_feedback f ON p.id = f.professeur_id AND f.cours_id = c.id
        WHERE c.filiere_id = %s
        GROUP BY p.id, p.nom, p.prenom, p.email
    """, (user_filiere_id,))
    professeur_data = cursor.fetchall()
    
    # 4. Récupérer les informations de la filière du chef
    cursor.execute("""
        SELECT f.id, f.nom, f.description,
               COUNT(DISTINCT u.id) as nb_etudiants,
               COUNT(DISTINCT c.id) as nb_cours
        FROM appcours_filiere f
        LEFT JOIN appcours_utilisateur u ON f.id = u.filiere_id AND u.role = 'etudiant'
        LEFT JOIN appcours_cours c ON f.id = c.filiere_id
        WHERE f.id = %s
        GROUP BY f.id, f.nom, f.description
    """, (user_filiere_id,))
    filiere_data = cursor.fetchall()
    
else:
    # Si pas de filière définie, récupérer toutes les données (cas d'erreur)
    cursor.execute("""
        SELECT c.id, c.nom, f.nom as filiere_nom 
        FROM appcours_cours c
        LEFT JOIN appcours_filiere f ON c.filiere_id = f.id
    """)
    cours_data = cursor.fetchall()
    
    cursor.execute("""
        SELECT 
            f.id,
            f.commentaire,
            f.note,
            f.cours_id,
            f.professeur_id,
            f.etudiant_id,
            f.date_creation,
            f.sentiment,
            f.suggestions,
            f.anonyme,
            f.partager,
            c.nom as cours_nom,
            fi.nom as filiere_nom,
            p.nom as prof_nom,
            p.prenom as prof_prenom,
            u.first_name as etudiant_prenom,
            u.last_name as etudiant_nom
        FROM appcours_feedback f
        LEFT JOIN appcours_cours c ON f.cours_id = c.id
        LEFT JOIN appcours_filiere fi ON c.filiere_id = fi.id
        LEFT JOIN appcours_professeur p ON f.professeur_id = p.id
        LEFT JOIN appcours_utilisateur u ON f.etudiant_id = u.id
    """)
    feedback_data = cursor.fetchall()
    
    cursor.execute("""
        SELECT p.id, p.nom, p.prenom, p.email,
               COUNT(DISTINCT pc.cours_id) as nb_cours,
               AVG(f.note) as note_moyenne
        FROM appcours_professeur p
        LEFT JOIN appcours_professeur_cours pc ON p.id = pc.professeur_id
        LEFT JOIN appcours_feedback f ON p.id = f.professeur_id
        GROUP BY p.id, p.nom, p.prenom, p.email
    """)
    professeur_data = cursor.fetchall()
    
    cursor.execute("""
        SELECT f.id, f.nom, f.description,
               COUNT(DISTINCT u.id) as nb_etudiants,
               COUNT(DISTINCT c.id) as nb_cours
        FROM appcours_filiere f
        LEFT JOIN appcours_utilisateur u ON f.id = u.filiere_id AND u.role = 'etudiant'
        LEFT JOIN appcours_cours c ON f.id = c.filiere_id
        GROUP BY f.id, f.nom, f.description
    """)
    filiere_data = cursor.fetchall()

# Organiser les données des feedbacks
df_feedback = pd.DataFrame(
    feedback_data, 
    columns=['id', 'commentaire', 'note', 'cours_id', 'professeur_id', 'etudiant_id', 
             'date_creation', 'sentiment', 'suggestions', 'anonyme', 'partager',
             'cours_nom', 'filiere_nom', 'prof_nom', 'prof_prenom', 
             'etudiant_prenom', 'etudiant_nom']
)

# Organiser les données des filières
df_filieres = pd.DataFrame(
    filiere_data,
    columns=['id', 'nom', 'description', 'nb_etudiants', 'nb_cours']
)

# Organiser les données des professeurs
df_professeurs = pd.DataFrame(
    professeur_data,
    columns=['id', 'nom', 'prenom', 'email', 'nb_cours', 'note_moyenne']
)

# Calcul des statistiques globales (maintenant filtrées par filière)
total_feedbacks = len(df_feedback)
note_moyenne = df_feedback['note'].mean() if not df_feedback.empty else 0

# Les données sont déjà filtrées, pas besoin de refiltrer
df_feedback_filiere = df_feedback

# Simuler un changement de performance
previous_avg = note_moyenne * 0.92 if note_moyenne > 0 else 0
avg_change_pct = ((note_moyenne - previous_avg) / previous_avg) * 100 if previous_avg > 0 else 0

# Classification par niveau
niveau_counts = {
    'Faible': 0,
    'Moyen': 0,
    'Excellent': 0
}

if not df_feedback.empty:
    niveau_counts = {
        'Faible': len(df_feedback[df_feedback['note'] <= 3]),
        'Moyen': len(df_feedback[(df_feedback['note'] > 3) & (df_feedback['note'] <= 4)]),
        'Excellent': len(df_feedback[df_feedback['note'] > 4])
    }

# Analyse des sentiments
sentiment_counts = {'positif': 0, 'neutre': 0, 'négatif': 0}

if not df_feedback.empty:
    # Compter les sentiments avec gestion des variantes
    for _, row in df_feedback.iterrows():
        sentiment = str(row['sentiment']).lower() if pd.notna(row['sentiment']) else 'neutre'
        if 'positif' in sentiment or 'positive' in sentiment:
            sentiment_counts['positif'] += 1
        elif 'négatif' in sentiment or 'negatif' in sentiment or 'negative' in sentiment:
            sentiment_counts['négatif'] += 1
        else:
            sentiment_counts['neutre'] += 1

# Moyenne par cours avec informations étendues
cours_stats = pd.DataFrame(columns=['cours', 'filiere', 'note_moyenne', 'nb_feedbacks', 'sentiment_dominant'])

if not df_feedback.empty and 'cours_nom' in df_feedback.columns and 'filiere_nom' in df_feedback.columns:
    # Vérifier que les colonnes nécessaires existent et ne sont pas toutes nulles
    if df_feedback['cours_nom'].notna().any() and df_feedback['filiere_nom'].notna().any():
        cours_stats = df_feedback.groupby(['cours_nom', 'filiere_nom']).agg({
            'note': ['mean', 'count'],
            'sentiment': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'neutre'
        }).reset_index()
        cours_stats.columns = ['cours', 'filiere', 'note_moyenne', 'nb_feedbacks', 'sentiment_dominant']
        cours_stats = cours_stats.sort_values('note_moyenne', ascending=False)

# Analyse des tendances temporelles - Version simplifiée
current_date = datetime.now()
trend_30d = trend_prev_30d = trend_change = 0
df_recent = pd.DataFrame()

if not df_feedback.empty and 'date_creation' in df_feedback.columns:
    try:
        df_feedback['date_creation'] = pd.to_datetime(df_feedback['date_creation']).dt.tz_localize(None)
        current_date = pd.Timestamp.now().tz_localize(None)
        
        last_30_days = df_feedback[df_feedback['date_creation'] >= (current_date - timedelta(days=30))]
        previous_30_days = df_feedback[
            (df_feedback['date_creation'] >= (current_date - timedelta(days=60))) &
            (df_feedback['date_creation'] < (current_date - timedelta(days=30)))
        ]
        
        trend_30d = last_30_days['note'].mean() if not last_30_days.empty else 0
        trend_prev_30d = previous_30_days['note'].mean() if not previous_30_days.empty else 0
        trend_change = ((trend_30d - trend_prev_30d) / trend_prev_30d * 100) if trend_prev_30d else 0
        
        # Derniers feedbacks récents avec création des colonnes manquantes
        df_recent = df_feedback.sort_values('date_creation', ascending=False).head(10).copy()
        df_recent['date_str'] = df_recent['date_creation'].dt.strftime('%d/%m/%Y')
        
        # Créer les colonnes d'affichage manquantes
        df_recent['etudiant_display'] = df_recent.apply(
            lambda row: f"{row['etudiant_prenom']} {row['etudiant_nom']}" 
            if pd.notna(row['etudiant_prenom']) and pd.notna(row['etudiant_nom']) 
            else "Anonyme", axis=1
        )
        
        df_recent['professeur_display'] = df_recent.apply(
            lambda row: f"{row['prof_prenom']} {row['prof_nom']}" 
            if pd.notna(row['prof_prenom']) and pd.notna(row['prof_nom']) 
            else "Non spécifié", axis=1
        )
        
    except Exception as e:
        print(f"Erreur dans l'analyse temporelle: {e}")
        trend_30d = trend_prev_30d = trend_change = 0
        df_recent = pd.DataFrame()

# Statistiques par professeur
top_professeurs = pd.DataFrame()
professeurs_a_ameliorer = pd.DataFrame()

if not df_professeurs.empty:
    df_professeurs['note_moyenne'] = df_professeurs['note_moyenne'].fillna(0)
    top_professeurs = df_professeurs.sort_values('note_moyenne', ascending=False).head(5)
    professeurs_a_ameliorer = df_professeurs[df_professeurs['note_moyenne'] < 3].sort_values('note_moyenne').head(5)


# Application Dash
external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Couleurs personnalisées
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

# Layout de l'application
app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '20px', 'fontFamily': 'Arial'}, children=[
    # En-tête avec informations utilisateur
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 
                  'backgroundColor': colors['card'], 'padding': '15px 20px', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}, children=[
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            html.I( style={'fontSize': '24px', 'color': colors['primary'], 'marginRight': '15px'}),
            html.Div([
                html.H1("Dashboard Analyse des Feedbacks", style={'margin': '0', 'color': colors['primary'], 'fontSize': '24px'}),
                html.P("Tableau de bord d'analyse des feedbacks étudiants", style={'margin': '5px 0 0 0', 'color': '#666'})
            ])
        ]),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            html.Div([
                html.P(f"Bonjour {user_name}", style={'fontWeight': 'bold', 'margin': '0', 'textAlign': 'right'}),
                html.P(user_email, style={'margin': '0', 'color': '#666', 'fontSize': '14px'})
            ]),
            html.I(className="fas fa-user-circle", style={'fontSize': '32px', 'marginLeft': '10px', 'color': colors['primary']})
        ])
    ]),
    
    # Rangée des statistiques clés (KPI)
html.Div(style={
    'display': 'grid',
    'gridTemplateColumns': 'repeat(auto-fit, minmax(280px, 1fr))',
    'gap': '20px',
    'marginBottom': '30px'
}, children=[
    # KPI: Total des feedbacks
    html.Div(style={
        'backgroundColor': colors['card'],
        'borderRadius': '12px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.05)',
        'padding': '25px',
        'border': f'3px solid {colors["primary"]}',
    }, children=[
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginBottom': '10px'
        }, children=[
            html.Div("Total Feedbacks", style={
                'color': colors['subtext'],
                'fontSize': '14px',
                'fontWeight': '500'
            }),
            html.Span("+12.4%", style={
                'color': colors['positive'], 
                'fontWeight': 'bold', 
                'fontSize': '14px',
                'backgroundColor': 'rgba(76, 175, 80, 0.1)',
                'padding': '4px 8px',
                'borderRadius': '4px'
            })
        ]),
        html.Div(style={
            'fontSize': '32px',
            'fontWeight': '700',
            'color': colors['primary'],
            'marginBottom': '5px'
        }, children=f"{total_feedbacks}"),
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'color': colors['subtext']
        }, children=[
            html.Span(f"Sentiment positif: {sentiment_counts.get('positif', 0)}")
        ])
    ]),
    
    # KPI: Note Moyenne
    html.Div(style={
        'backgroundColor': colors['card'],
        'borderRadius': '12px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.05)',
        'padding': '25px',
        'border': f'3px solid {colors["secondary"]}',
    }, children=[
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginBottom': '10px'
        }, children=[
            html.Div("Note Moyenne", style={
                'color': colors['subtext'],
                'fontSize': '14px',
                'fontWeight': '500'
            }),
            html.Span(f"+{avg_change_pct:.1f}%", style={
                'color': colors['positive'], 
                'fontWeight': 'bold', 
                'fontSize': '14px',
                'backgroundColor': 'rgba(76, 175, 80, 0.1)',
                'padding': '4px 8px',
                'borderRadius': '4px'
            })
        ]),
        html.Div(style={
            'fontSize': '32px',
            'fontWeight': '700',
            'color': colors['secondary'],
            'marginBottom': '5px'
        }, children=f"{note_moyenne:.1f}/5"),
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'color': colors['subtext']
        }, children=[
            html.Span(f"Évolution sur 30j: {trend_change:.1f}%")
        ])
    ]),
    
    # KPI: Niveaux de Satisfaction
    html.Div(style={
        'backgroundColor': colors['card'],
        'borderRadius': '12px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.05)',
        'padding': '25px',
        'border': f'3px solid {colors["success"]}',
    }, children=[
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginBottom': '10px'
        }, children=[
            html.Div("Satisfaction Excellente", style={
                'color': colors['subtext'],
                'fontSize': '14px',
                'fontWeight': '500'
            }),
            html.Span("+5.2%", style={
                'color': colors['positive'], 
                'fontWeight': 'bold', 
                'fontSize': '14px',
                'backgroundColor': 'rgba(76, 175, 80, 0.1)',
                'padding': '4px 8px',
                'borderRadius': '4px'
            })
        ]),
        html.Div(style={
            'fontSize': '32px',
            'fontWeight': '700',
            'color': colors['success'],
            'marginBottom': '5px'
        }, children=f"{niveau_counts.get('Excellent', 0)}"),
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'color': colors['subtext']
        }, children=[
            html.Span(f"Sur {total_feedbacks} feedbacks")
        ])
    ]),
    
    # KPI: Nombre de filières/professeurs
    html.Div(style={
        'backgroundColor': colors['card'],
        'borderRadius': '12px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.05)',
        'padding': '25px',
        'border': f'3px solid {colors["info"]}',
    }, children=[
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginBottom': '10px'
        }, children=[
            html.Div("Filières Actives", style={
                'color': colors['subtext'],
                'fontSize': '14px',
                'fontWeight': '500'
            }),
            html.Span(f"{len(df_professeurs)} profs", style={
                'color': colors['info'], 
                'fontWeight': 'bold', 
                'fontSize': '14px',
                'backgroundColor': 'rgba(33, 150, 243, 0.1)',
                'padding': '4px 8px',
                'borderRadius': '4px'
            })
        ]),
        html.Div(style={
            'fontSize': '32px',
            'fontWeight': '700',
            'color': colors['info'],
            'marginBottom': '5px'
        }, children=f"{len(df_filieres)}"),
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'color': colors['subtext']
        }, children=[
            html.Span(f"Total étudiants: {df_filieres['nb_etudiants'].sum()}")
        ])
    ]),
]),
    # Rangée principale des graphiques et tableaux
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
        # Colonne de gauche (40%)
        html.Div(style={'flex': '4', 'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
            # Graphique combiné sentiments et niveaux
            html.Div(style={'backgroundColor': colors['card'], 'padding': '15px', 'borderRadius': '8px',
                           'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                html.H3("Analyse Sentiments & Niveaux", style={'margin': '0 0 15px 0', 'fontSize': '18px', 'color': colors['text']}),
                dcc.Graph(
                    figure=go.Figure(data=[
                        # Barres pour les sentiments
                        go.Bar(
                            name='Sentiments',
                            x=list(sentiment_counts.keys()),
                            y=list(sentiment_counts.values()),
                            marker_color=['#6E67FF', '#6E67FF', "#6E67FF"],  # vert, orange, rouge
                            offsetgroup=1
                        ),
                        # Barres pour les niveaux
                        go.Bar(
                            name='Niveaux',
                            x=list(niveau_counts.keys()),
                            y=list(niveau_counts.values()),
                            marker_color=["#FC67FA", '#FC67FA', '#FC67FA'],  # rouge, orange, vert
                            offsetgroup=2
                        )
                    ]).update_layout(
                        barmode='group',
                        height=250,
                        margin=dict(l=40, r=20, t=10, b=30),
                        xaxis_title="Catégories",
                        yaxis_title="Nombre",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                ) if sentiment_counts and niveau_counts else html.P("Aucune donnée disponible")
            ]),
            
            # Graphique des notes par filière
            html.Div(style={'backgroundColor': colors['card'], 'padding': '15px', 'borderRadius': '8px',
                           'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                html.H3("Performance par Filière", style={'margin': '0 0 15px 0', 'fontSize': '18px', 'color': colors['text']}),
                dcc.Graph(
                    figure=px.box(
                        df_feedback,
                        x='filiere_nom' if 'filiere_nom' in df_feedback.columns else None, 
                        y='note' if 'note' in df_feedback.columns else None,
                        height=250,
                        title=""
                    ).update_layout(
                        margin=dict(l=40, r=20, t=10, b=30),
                        xaxis_title="Filière",
                        yaxis_title="Note"
                    )
                ) if not df_feedback.empty and 'filiere_nom' in df_feedback.columns and 'note' in df_feedback.columns else html.P("Données insuffisantes pour afficher le graphique par filière")
            ]),
        ]),
        
        # Colonne de droite (60%)
html.Div(style={'flex': '6', 'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
    # Top Cours par Moyenne
    html.Div(style={
        'backgroundColor': colors['card'], 
        'padding': '15px', 
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }, children=[
        html.H3("Top Cours par Moyenne", style={
            'margin': '0 0 15px 0', 
            'fontSize': '18px', 
            'color': colors['text']
        }),
        dcc.Graph(
            figure=px.bar(
                cours_stats.head(5) if not cours_stats.empty else pd.DataFrame(),
                x='note_moyenne', 
                y='cours',
                orientation='h',
                height=250,
                hover_data=['filiere', 'nb_feedbacks']
            ).update_traces(
                marker_color='#C8A8E9'  # Couleur unique pour toutes les barres
            ).update_layout(
                margin=dict(l=40, r=20, t=10, b=30),
                yaxis={'categoryorder': 'total ascending'},
                yaxis_title="",
                xaxis_title="Note moyenne"
            )
        ) if not cours_stats.empty else html.P("Aucune donnée disponible")
    ]),
            
            # Tableau des feedbacks récents
            html.Div(style={'backgroundColor': colors['card'], 'padding': '15px', 'borderRadius': '8px',
                           'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '15px'}, children=[
                    html.H3("Feedbacks Récents", style={'margin': '0', 'fontSize': '18px', 'color': colors['text']}),
                    html.Div(style={'backgroundColor': colors['info'], 'color': 'white', 'padding': '5px 10px', 
                                   'borderRadius': '4px', 'fontSize': '12px'}, children="Voir tout")
                ]),
                dash_table.DataTable(
                    data=df_recent[['cours_nom', 'commentaire', 'note', 'date_str', 'sentiment', 'etudiant_display', 'professeur_display']].rename(
                        columns={
                            'cours_nom': 'Cours', 
                            'commentaire': 'Feedback', 
                            'note': 'Note', 
                            'date_str': 'Date',
                            'sentiment': 'Sentiment',
                            'etudiant_display': 'Étudiant',
                            'professeur_display': 'Professeur'
                        }
                    ).to_dict('records') if not df_recent.empty else [],
                    columns=[
                        {'name': 'Cours', 'id': 'Cours'},
                        {'name': 'Feedback', 'id': 'Feedback'},
                        {'name': 'Sentiment', 'id': 'Sentiment'},
                        {'name': 'Professeur', 'id': 'Professeur'},
                        {'name': 'Date', 'id': 'Date'},
                    ],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'fontFamily': 'Arial',
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'maxWidth': '150px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    },
                    style_header={
                        'backgroundColor': '#f1f1f1',
                        'fontWeight': 'bold',
                        'borderBottom': '1px solid #ddd',
                    },
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{Note} >= 4'},
                            'backgroundColor': '#E3AADD',
                        },
                        {
                            'if': {'filter_query': '{Note} < 3'},
                            'backgroundColor': "#F4F1FD",
                        },
                        {
                            'if': {'filter_query': '{Sentiment} = positif'},
                            'color': "#050304",
                        },
                        {
                            'if': {'filter_query': '{Sentiment} = négatif'},
                            'color': "#050304",
                        }
                    ],
                    page_size=3,
                )
            ]),
        ]),
    ]),
    
    # Container principal
html.Div(children=[
    
    # Première ligne - Tables des professeurs et filières
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginTop': '20px'}, children=[
        
        # Performance des professeurs
        html.Div(style={
            'flex': '1', 
            'backgroundColor': colors['card'], 
            'padding': '20px', 
            'borderRadius': '12px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'border': '1px solid #e0e0e0'
        }, children=[
            html.H3(" Top Professeurs", style={
                'margin': '0 0 20px 0', 
                'fontSize': '20px', 
                'color': colors['text'],
                'fontWeight': 'bold',
                'textAlign': 'center'
            }),
            dash_table.DataTable(
                data=top_professeurs[['prenom', 'nom', 'note_moyenne', 'nb_cours']].rename(
                    columns={
                        'prenom': 'Prénom',
                        'nom': 'Nom', 
                        'note_moyenne': 'Note Moy.',
                        'nb_cours': 'Nb Cours'
                    }
                ).to_dict('records') if not top_professeurs.empty else [],
                columns=[
                    {'name': 'Prénom', 'id': 'Prénom'},
                    {'name': 'Nom', 'id': 'Nom'},
                    {'name': 'Note Moy.', 'id': 'Note Moy.', 'type': 'numeric', 'format': dict(specifier='.1f')},
                    {'name': 'Nb Cours', 'id': 'Nb Cours', 'type': 'numeric'},
                ],
                style_table={
                    'overflowX': 'auto',
                    'borderRadius': '8px',
                    'border': '1px solid #ddd'
                },
                style_cell={
                    'textAlign': 'center',
                    'padding': '12px 8px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '13px',
                    'border': '1px solid #e0e0e0'
                },
                style_header={
                    'backgroundColor': '#feebff',
                    'fontWeight': 'bold',
                    'color': '#333',
                    'borderBottom': '2px solid #ddd',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{Note Moy.} >= 4.0'},
                        'backgroundColor': 'rgba(76, 175, 80, 0.15)',
                        'color': '#2e7d32',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {'filter_query': '{Note Moy.} >= 3.5 && {Note Moy.} < 4.0'},
                        'backgroundColor': 'rgba(255, 193, 7, 0.15)',
                        'color': '#f57f17'
                    }
                ],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                }
            )
        ]),
        
        # Statistiques par filière
        html.Div(style={
            'flex': '1', 
            'backgroundColor': colors['card'], 
            'padding': '20px', 
            'borderRadius': '12px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'border': '1px solid #e0e0e0'
        }, children=[
            html.H3(" Statistiques par Filière", style={
                'margin': '0 0 20px 0', 
                'fontSize': '20px', 
                'color': colors['text'],
                'fontWeight': 'bold',
                'textAlign': 'center'
            }),
            dash_table.DataTable(
                data=df_filieres[['nom', 'nb_etudiants', 'nb_cours']].rename(
                    columns={
                        'nom': 'Filière',
                        'nb_etudiants': 'Étudiants',
                        'nb_cours': 'Cours'
                    }
                ).to_dict('records') if not df_filieres.empty else [],
                columns=[
                    {'name': 'Filière', 'id': 'Filière'},
                    {'name': 'Étudiants', 'id': 'Étudiants', 'type': 'numeric'},
                    {'name': 'Cours', 'id': 'Cours', 'type': 'numeric'},
                ],
                style_table={
                    'overflowX': 'auto',
                    'borderRadius': '8px',
                    'border': '1px solid #ddd'
                },
                style_cell={
                    'textAlign': 'center',
                    'padding': '12px 8px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '13px',
                    'border': '1px solid #e0e0e0'
                },
                style_header={
                    'backgroundColor': '#feebff',
                    'fontWeight': 'bold',
                    'color': '#333',
                    'borderBottom': '2px solid #ddd',
                    'textAlign': 'center'
                },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{Étudiants} >= 100'},
                        'backgroundColor': 'rgba(33, 150, 243, 0.15)',
                        'color': '#1565c0',
                        'fontWeight': 'bold'
                    }
                ]
            )
        ])
    ]),
    
    # Deuxième ligne - Suggestions d'amélioration
    html.Div(style={'marginTop': '20px'}, children=[
        html.Div(style={
            'backgroundColor': colors['card'], 
            'padding': '20px', 
            'borderRadius': '12px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'border': '1px solid #e0e0e0'
        }, children=[
            html.H3("Suggestions d'Amélioration", style={
                'margin': '0 0 20px 0', 
                'fontSize': '20px', 
                'color': colors['text'],
                'fontWeight': 'bold',
                'textAlign': 'center'
            }),
            html.Div(style={'maxHeight': '300px', 'overflowY': 'auto'}, children=[
                html.Div(style={
                    'padding': '15px', 
                    'backgroundColor': "#dfcdff", 
                    'marginBottom': '15px', 
                    'borderRadius': '8px', 
                    'border': '1px solid #D661F9'
                }, children=[
                    html.Div(style={
                        'fontWeight': 'bold', 
                        'marginBottom': '8px', 
                        'color': "#620565",
                        'fontSize': '16px'
                    }, children=[
                        html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                        "Feedbacks négatifs"
                    ]),
                    html.P(f"Analyser les {sentiment_counts.get('négatif', 0)} feedbacks négatifs pour identifier les problèmes récurrents", 
                           style={'margin': '0', 'fontSize': '14px', 'color': "#620565"})
                ]),
                html.Div(style={
                    'padding': '15px', 
                    'backgroundColor': "#fae0f7", 
                    'marginBottom': '15px', 
                    'borderRadius': '8px',
                    'border': '1px solid #fae0f7'
                }, children=[
                    html.Div(style={
                        'fontWeight': 'bold', 
                        'marginBottom': '8px',
                        'color': '#1565c0',
                        'fontSize': '16px'
                    }, children=[
                        html.I(className="fas fa-chart-line", style={'marginRight': '8px'}),
                        "Cours mal notés"
                    ]),
                    html.P("Organiser des sessions supplémentaires pour les cours ayant une note moyenne inférieure à 6/10", 
                           style={'margin': '0', 'fontSize': '14px', 'color': '#1565c0'})
                ]),
                html.Div(style={
                    'padding': '15px', 
                    'backgroundColor': '#e8f5e8', 
                    'borderRadius': '8px',
                    'border': '1px solid #4caf50'
                }, children=[
                    html.Div(style={
                        'fontWeight': 'bold', 
                        'marginBottom': '8px',
                        'color': '#2e7d32',
                        'fontSize': '16px'
                    }, children=[
                        html.I(className="fas fa-sync-alt", style={'marginRight': '8px'}),
                        "Amélioration continue"
                    ]),
                    html.P("Mettre en place un suivi hebdomadaire des feedbacks pour réagir plus rapidement", 
                           style={'margin': '0', 'fontSize': '14px', 'color': '#2e7d32'})
                ]),
            ])
        ])
    ])
]),
    
    # Pied de page
    html.Footer(style={
        'textAlign': 'center',
        'padding': '20px 0',
        'marginTop': '20px',
        'borderTop': '1px solid #ddd',
        'color': '#666',
        'fontSize': '14px'
    }, children=[
        "© 2025 Feedback Analysis Dashboard - Dernière mise à jour: " + datetime.now().strftime("%d/%m/%Y")
    ])
])
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)