from django.db.models import Avg
import pandas as pd
import plotly.express as px
import dash as dcc
import dash as html
import plotly.graph_objects as go
from dash import dcc, html, dash_table, callback
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output
from django.db.models import Avg
from appcours.models import (
    Utilisateur, Filiere, Promotion, Cours, 
    Professeur, Feedback, CourseResource, Notes, ModeEvaluation
)
def get_etudiant_info(etudiant_id):
    """Récupère les informations de l'étudiant connecté"""
    try:
        print(f"Recherche de l'étudiant avec ID: {etudiant_id}")
        etudiant = Utilisateur.objects.filter(id=etudiant_id, role='etudiant').first()
        if not etudiant:
            print(f"Aucun étudiant trouvé avec l'ID: {etudiant_id}")
            return None
        
        filiere_nom = etudiant.filiere.nom if etudiant.filiere else None
        print(f"Étudiant trouvé: {etudiant.first_name} {etudiant.last_name}, email: {etudiant.email}")
        
        return {
            'id': etudiant.id,
            'first_name': etudiant.first_name,
            'last_name': etudiant.last_name,
            'username': etudiant.username,
            'email': etudiant.email,
            'role': etudiant.role,
            'filiere_id': etudiant.filiere.id if etudiant.filiere else None,
            'filiere_nom': filiere_nom,
            'promotion_id': etudiant.promotion.id if etudiant.promotion else None,
            'promotion_nom': etudiant.promotion.nom if etudiant.promotion else None
        }
    except Exception as e:
        print(f"Exception lors de la récupération de l'étudiant: {str(e)}")
        return None

def get_cours_filiere(filiere_id):
    if not filiere_id:
        return []
    cours_list = Cours.objects.filter(filiere_id=filiere_id).prefetch_related('professeurs')
    cours_filiere = []
    for cours in cours_list:
        professeurs = cours.professeurs.all()
        profs_data = []
        for prof in professeurs:
            profs_data.append({
                'prof_id': prof.id,
                'prof_prenom': prof.prenom,
                'prof_nom': prof.nom,
                'prof_email': prof.email,
            })
        cours_data = {
            'cours_id': cours.id,
            'cours_nom': cours.nom,
            'filiere_nom': cours.filiere.nom,
            'professeurs': profs_data,
        }
        cours_filiere.append(cours_data)
    return cours_filiere

def get_ressources_cours(cours_nom):
    try:
        ressources = CourseResource.objects.filter(course_name=cours_nom)
        return [
            {
                'course_name': r.course_name,
                'resource_link': r.resource_link,
                'description': r.description
            }
            for r in ressources
        ]
    except Exception as e:
        print(f"Erreur lors de la récupération des ressources: {e}")
        return []

def get_notes_etudiant(etudiant_id):
    try:
        notes = Notes.objects.filter(etudiant_id=etudiant_id).select_related('cours')
        notes_par_cours = {}
        for note in notes:
            cours_id = note.cours.id
            if cours_id not in notes_par_cours:
                notes_par_cours[cours_id] = {
                    'cours_id': cours_id,
                    'nom': note.cours.nom,
                    'notes': []
                }
            notes_par_cours[cours_id]['notes'].append(float(note.note))
        
        result = []
        for cours_data in notes_par_cours.values():
            moyenne_note_cours = sum(cours_data['notes']) / len(cours_data['notes'])
            result.append({
                'cours_id': cours_data['cours_id'],
                'nom': cours_data['nom'],
                'moyenne_note_cours': moyenne_note_cours
            })
        return result
    except Exception as e:
        print(f"Erreur lors de la récupération des notes: {e}")
        return []
def get_notes_classe():
    try:
        notes = Notes.objects.values('cours_id', 'cours__nom').annotate(
            moyenne_classe=Avg('note')
        ).order_by('cours_id')
        
        return [
            {
                'cours_id': note['cours_id'],
                'cours_nom': note['cours__nom'],
                'moyenne_classe': float(note['moyenne_classe'])
            }
            for note in notes
        ]
    except Exception as e:
        print(f"Erreur lors de la récupération des moyennes de classe: {e}")
        return []
def get_modes_evaluation_cours(filiere_id):
    try:
        if not filiere_id:
            return []

        cours_list = Cours.objects.filter(filiere_id=filiere_id)
        evaluations_data = []

        for cours in cours_list:
            modes = ModeEvaluation.objects.filter(cours=cours)
            if modes.exists():
                cours_evaluations = {
                    'cours_nom': cours.nom,
                    'modes': []
                }
                for mode in modes:
                    cours_evaluations['modes'].append({
                        'type': mode.mode,
                        'pourcentage': mode.pourcentage
                    })
                evaluations_data.append(cours_evaluations)

        print("Données récupérées pour Dash:", evaluations_data)
        return evaluations_data
    except Exception as e:
        print(f"Erreur lors de la récupération des modes d'évaluation: {e}")
        return []
def get_notes_et_moyennes(etudiant_id):
    data = []
    qs = Notes.objects.filter(etudiant_id=etudiant_id).select_related('cours')
    for note_obj in qs:
        cours = note_obj.cours
        student_note = float(note_obj.note)
        moy = (
            Notes.objects
                 .filter(cours=cours)
                 .aggregate(avg_note=Avg('note'))
                 .get('avg_note') or 0
        )
        data.append({
            'Cours': cours.nom,
            'Cours_id': cours.id,
            'Notes': round(student_note, 2),
            'Moyenne Classe': round(moy, 2),
        })
    return data
colors_list = ['#d7bde2', '#fadbd8', '#fb95f3']
def create_notes_graph(df_notes, colors):
    if df_notes.empty:
        return go.Figure(
            layout=go.Layout(
                title="Aucune note disponible",
                margin=dict(l=40, r=40, t=40, b=80),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400,
                annotations=[
                    dict(
                       text="Aucune note trouvée pour cet étudiant",
                       xref="paper", yref="paper",
                       x=0.5, y=0.5, xanchor='center', yanchor='middle',
                       showarrow=False, font=dict(size=16, color='#718096')
                    )
                ]
            )
        )
    return go.Figure(
        data=[
            go.Scatter(
                x=df_notes['Cours'],
                y=df_notes['Notes'],
                mode='lines+markers',
                name='Vos notes',
                line=dict(width=3, color=colors['primary']),
                marker=dict(size=10, color=colors['primary']),
                fill='tozeroy',
                fillcolor='rgba(110, 103, 255, 0.1)'
            ),
            go.Scatter(
               x=df_notes['Cours'],
               y=df_notes['Moyenne Classe'],
               mode='lines+markers',
               name='Moyenne de la classe',
               line=dict(width=3, color=colors['secondary'], dash='dot'),
                marker=dict(size=10, color=colors['secondary'])
            )
        ],
        layout=go.Layout(
            margin=dict(l=40, r=40, t=40, b=80),
            legend=dict(
               orientation="h",
               yanchor="bottom",
               y=1.02,
               xanchor="right",
               x=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=False,
                tickangle=45,
                title="Cours"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#f5f5f5',
                title="Notes /20",
                range=[0, 20]
            ),
            height=400
        )
     )
def create_evaluation_charts(evaluations_data, colors):
    if not evaluations_data:
        return html.Div([
            html.P("Aucun mode d'évaluation trouvé", style={
                'color': colors['subtext'],
                'textAlign': 'center',
                'padding': '40px'
            })
        ])
    charts = []
    for cours_data in evaluations_data:
        labels = [mode['type'] for mode in cours_data['modes']]
        values = [mode['pourcentage'] for mode in cours_data['modes']]

        fig = go.Figure(
            data=[go.Pie(
                labels=labels,
                values=values,
                textinfo='label+percent',
                textfont={'size': 12},
                marker=dict(
                    colors=['#d7bde2', '#fadbd8', '#f8b3f3', '#EF4444', '#8B5CF6'],
                    line=dict(width=2, color='white')
                )
            )],
            layout=go.Layout(
                title=f"Répartition des modes d'évaluation - {cours_data['cours_nom']}",
                margin=dict(t=50, b=20, l=20, r=20),
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
        )
        charts.append(
            html.Div([
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ], style={'marginBottom': '20px'})
        )
        print("Éléments HTML retournés : ", charts)
    return html.Div(charts)


def create_student_dashboard(user_id, app_name='StudentDashboard'):
    """Crée le dashboard interactif pour l'étudiant"""
    # Créer une instance unique de l'app Dash
    try:
        app = DjangoDash.get_or_create(app_name)
    except:
        app = DjangoDash(app_name)
    
    # Récupération des données de l'étudiant
    etudiant = get_etudiant_info(user_id)
    if not etudiant:
        app.layout = html.Div([
            dbc.Alert([
                html.H4("❌ Erreur d'accès", className="alert-heading"),
                html.P("Étudiant non trouvé ou non autorisé"),
                html.Hr(),
                html.P("Veuillez vérifier que l'utilisateur existe et a le rôle 'etudiant'", 
                       className="mb-0")
            ], color="danger")
        ], style={'padding': '20px'})
        return app

    # Récupération des données
    cours_filiere = get_cours_filiere(etudiant.get('filiere_id'))
    data_notes = get_notes_et_moyennes(user_id)
    df_notes = pd.DataFrame(data_notes)
    
    if df_notes.empty:
        print("Aucune note trouvée pour cet étudiant")
        df_notes = pd.DataFrame(columns=['Cours', 'Notes', 'Moyenne Classe'])
    
    # Calculs statistiques
    moyenne_generale_etudiant = round(df_notes['Notes'].mean(), 2) if not df_notes.empty else 0
    moyenne_generale_classe = round(df_notes['Moyenne Classe'].mean(), 2) if not df_notes.empty else 0
    
    evaluations_data = get_modes_evaluation_cours(etudiant.get('filiere_id'))
    
    # Préparation des données pour les tableaux
    cours_data = []
    for cours in cours_filiere:
        ressources = get_ressources_cours(cours['cours_nom'])
        if cours['professeurs']:
            professeurs_noms = [f"{prof['prof_prenom']} {prof['prof_nom']}" for prof in cours['professeurs']]
            professeurs_emails = [prof['prof_email'] for prof in cours['professeurs']]
            professeur_str = "; ".join(professeurs_noms)
            email_str = "; ".join(professeurs_emails)
        else:
            professeur_str = "Non assigné"
            email_str = "Non disponible"
        
        cours_data.append({
            'Cours': cours['cours_nom'],
            'Professeur(s)': professeur_str,
            'Email(s) Prof': email_str,
            'Ressources': "; ".join([f"{r['description']}" for r in ressources]) if ressources else "Aucune ressource"
        })
    
    colors = {
        'primary': '#6E67FF',
        'secondary': '#FC67FA',
        'bg_color': '#F9FAFE',
        'card': '#FFFFFF',
        'text': '#2D3748',
        'subtext': '#718096',
        'border': '#E2E8F0',
        'success': '#10B981',
        'warning': '#F59E0B',
    }
    
    app.layout = html.Div(style={
        'backgroundColor': colors['bg_color'],
        'padding': '20px',
        'minHeight': '100vh',
        'fontFamily': 'Inter, sans-serif'
    }, children=[
        html.Div(style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'marginBottom': '30px',
            'backgroundColor': colors['card'],
            'padding': '20px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 15px rgba(0,0,0,0.05)'
        }, children=[
            html.Div(children=[
                html.H1("Tableau de bord étudiant", style={
                    'fontSize': '28px',
                    'fontWeight': '700',
                    'color': colors['primary'],
                    'margin': '0'
                }),
                html.P(f"Bienvenue, {etudiant.get('first_name', '')} {etudiant.get('last_name', '')}", style={
                    'color': colors['text'],
                    'fontSize': '16px',
                    'margin': '5px 0'
                }),
                html.P(f"Filière: {etudiant.get('filiere_nom', 'Non spécifiée')} | Promotion: {etudiant.get('promotion_nom', 'Non spécifiée')}", style={
                    'color': colors['subtext'],
                    'fontSize': '14px',
                    'margin': '0'
                })
            ])
        ]),     
        html.Div(style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(280px, 1fr))',
            'gap': '20px',
            'marginBottom': '30px'
        }, children=[
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
                    'marginBottom': '10px'
                }, children=[
                    html.Div("Votre moyenne générale", style={
                        'color': colors['subtext'],
                        'fontSize': '14px',
                        'fontWeight': '500'
                    })
                ]),
                html.Div(style={
                    'fontSize': '32px',
                    'fontWeight': '700',
                    'color': colors['primary'],
                    'marginBottom': '5px'
                }, children=f"{moyenne_generale_etudiant}/20"),
                html.Div(style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'color': colors['success'] if moyenne_generale_etudiant >= moyenne_generale_classe else colors['warning']
                }, children=[
                    html.Span(f"{'Au-dessus' if moyenne_generale_etudiant >= moyenne_generale_classe else 'En-dessous'} de la moyenne de classe")
                ])
            ]),
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
                    'marginBottom': '10px'
                }, children=[
                    html.Div("Moyenne de la classe", style={
                        'color': colors['subtext'],
                        'fontSize': '14px',
                        'fontWeight': '500'
                    })
                ]),
                html.Div(style={
                    'fontSize': '32px',
                    'fontWeight': '700',
                    'color': colors['secondary'],
                    'marginBottom': '5px'
                }, children=f"{moyenne_generale_classe}/20"),
                html.Div(style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'color': colors['subtext']
                }, children=[
                    html.Span("Performance globale")
                ])
            ]),
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
                    'marginBottom': '10px'
                }, children=[
                    html.Div("Cours cette année", style={
                        'color': colors['subtext'],
                        'fontSize': '14px',
                        'fontWeight': '500'
                    })
                ]),
                html.Div(style={
                    'fontSize': '32px',
                    'fontWeight': '700',
                    'color': colors['success'],
                    'marginBottom': '5px'
                }, children=str(len(cours_filiere))),
                html.Div(style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'color': colors['subtext']
                }, children=[
                    html.Span(f"Dans la filière {etudiant.get('filiere_nom', '')}")
                ])
            ]),
        ]),
        html.Div(style={
            'display': 'grid',
            'gridTemplateColumns': '2fr 1fr',
            'gap': '20px',
            'marginBottom': '30px'
        }, children=[
            html.Div([
                html.H2("Évolution des notes", style={
                    'fontSize': '20px',
                    'fontWeight': '600',
                    'marginBottom': '20px',
                    'color': colors['text']
                }),
                dcc.Graph(figure=create_notes_graph(df_notes, colors))
            ], style={
                'backgroundColor': colors['card'],
                'borderRadius': '12px',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.05)',
                'padding': '25px',
            }),
            html.Div(style={
                'backgroundColor': colors['card'],
                'borderRadius': '12px',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.05)',
                'padding': '25px',
            }, children=[
                html.H2("Statistiques rapides", style={
                    'fontSize': '20px',
                    'fontWeight': '600',
                    'marginBottom': '20px',
                    'color': colors['text']
                }),
                html.Div([
                    html.Div([
                        html.H3(f"{df_notes['Notes'].max():.1f}/20" if not df_notes.empty else "N/A", style={
                            'fontSize': '24px',
                            'fontWeight': '600',
                            'color': colors['success'],
                            'margin': '0'
                        }),
                        html.P("Meilleure note", style={
                            'color': colors['subtext'],
                            'fontSize': '12px',
                            'margin': '0'
                        })
                    ], style={'marginBottom': '15px'}),
                    
                    html.Div([
                        html.H3(f"{df_notes['Notes'].min():.1f}/20" if not df_notes.empty else "N/A", style={
                            'fontSize': '24px',
                            'fontWeight': '600',
                            'color': colors['warning'],
                            'margin': '0'
                        }),
                        html.P("Note la plus basse", style={
                            'color': colors['subtext'],
                            'fontSize': '12px',
                            'margin': '0'
                        })
                    ], style={'marginBottom': '15px'}),
                    
                    html.Div([
                        html.H3(f"{(df_notes['Notes'] >= 10).sum()}/{len(df_notes)}" if not df_notes.empty else "0/0", style={
                            'fontSize': '24px',
                            'fontWeight': '600',
                            'color': colors['primary'],
                            'margin': '0'
                        }),
                        html.P("Cours réussis", style={
                            'color': colors['subtext'],
                            'fontSize': '12px',
                            'margin': '0'
                        })
                    ]),
                ]) if not df_notes.empty else html.Div([
                    html.P("Aucune statistique disponible", style={
                        'color': colors['subtext'],
                        'textAlign': 'center',
                        'padding': '40px'
                    })
                ])
            ]),
        ]),
        html.Div(style={
            'backgroundColor': colors['card'],
            'borderRadius': '12px',
            'boxShadow': '0 4px 15px rgba(0,0,0,0.05)',
            'padding': '25px',
            'marginBottom': '30px'
        }, children=[
            html.H2("Modes d'évaluation par cours", style={
                'fontSize': '20px',
                'fontWeight': '600',
                'marginBottom': '20px',
                'color': colors['text']
            }),
            create_evaluation_charts(evaluations_data, colors)
        ]),
        
        dcc.Tabs(id='tabs', value='tab-1', style={
            'marginBottom': '10px'
        }, children=[
            dcc.Tab(label='📚 Cours & Ressources', value='tab-1', style={
                'padding': '12px 24px',
                'fontWeight': '500'
            }),
            dcc.Tab(label='👨‍🏫 Professeurs', value='tab-2', style={
                'padding': '12px 24px',
                'fontWeight': '500'
            }),
            dcc.Tab(label='📊 Détail des notes', value='tab-3', style={
                'padding': '12px 24px',
                'fontWeight': '500'
            }),

        ]),
        html.Div(id='tabs-content', style={
            'backgroundColor': colors['card'],
            'borderRadius': '12px',
            'boxShadow': '0 4px 15px rgba(0,0,0,0.05)',
            'padding': '25px',
        }),
    ])
    @app.callback(
        Output('tabs-content', 'children'),
        [Input('tabs', 'value')]
    )
    def render_content(tab):
      if tab == 'tab-1':
        df_cours_display = pd.DataFrame(cours_data)
        return html.Div([
            html.H3("Liste des cours et ressources", style={
                'color': colors['text'],
                'marginBottom': '20px'
            }),
            dash_table.DataTable(
                data=df_cours_display.to_dict('records') if not df_cours_display.empty else [],
                columns=[{'name': i, 'id': i} for i in df_cours_display.columns] if not df_cours_display.empty else [],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '15px',
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '14px',
                    'border': 'none',
                    'borderBottom': '1px solid #E2E8F0'
                },
                style_header={
                    'backgroundColor': colors['bg_color'],
                    'fontWeight': '600',
                    'border': 'none',
                    'borderBottom': '2px solid #E2E8F0',
                    'color': colors['text']
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': colors['bg_color']
                    }
                ],
                page_size=10
            ) if not df_cours_display.empty else html.P("Aucun cours trouvé pour cette filière", style={
                'color': colors['subtext'],
                'textAlign': 'center',
                'padding': '40px'
            })
        ])
      elif tab == 'tab-2':
        professeurs_data = []
        professeurs_vus = set()
        for cours in cours_filiere:
            for prof in cours['professeurs']:
                prof_id = prof['prof_id']
                if prof_id not in professeurs_vus:
                    professeurs_vus.add(prof_id)
                    cours_prof = [c['cours_nom'] for c in cours_filiere 
                                 if any(p['prof_id'] == prof_id for p in c['professeurs'])]
                    professeurs_data.append({
                        'Prénom': prof['prof_prenom'],
                        'Nom': prof['prof_nom'],
                        'Email': prof['prof_email'],
                        'Cours enseignés': '; '.join(cours_prof)
                    })
        df_profs = pd.DataFrame(professeurs_data)
        return html.Div([
            html.H3("Liste des professeurs", style={
                'color': colors['text'],
                'marginBottom': '20px'
            }),
            dash_table.DataTable(
                data=df_profs.to_dict('records') if not df_profs.empty else [],
                columns=[{'name': i, 'id': i} for i in df_profs.columns] if not df_profs.empty else [],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '15px',
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '14px',
                    'border': 'none',
                    'borderBottom': '1px solid #E2E8F0'
                },
                style_header={
                    'backgroundColor': colors['bg_color'],
                    'fontWeight': '600',
                    'border': 'none',
                    'borderBottom': '2px solid #E2E8F0',
                    'color': colors['text']
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': colors['bg_color']}
                ],
                page_size=5
            ) if not df_profs.empty else html.P("Aucun professeur trouvé", style={
                'color': colors['subtext'],
                'textAlign': 'center',
                'padding': '40px'
            })
        ])   
      elif tab == 'tab-3':
        return html.Div([
            html.H3("Détail des notes par cours", style={
                'color': colors['text'],
                'marginBottom': '20px'
            }),
            dash_table.DataTable(
                data=df_notes.to_dict('records') if not df_notes.empty else [],
                columns=[{'name': i, 'id': i} for i in df_notes.columns] if not df_notes.empty else [],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '15px',
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '14px',
                    'border': 'none',
                    'borderBottom': '1px solid #E2E8F0'
                },
                style_header={
                    'backgroundColor': colors['bg_color'],
                    'fontWeight': '600',
                    'border': 'none',
                    'borderBottom': '2px solid #E2E8F0',
                    'color': colors['text']
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': colors['bg_color']}
                ],
                page_size=5
            ) if not df_notes.empty else html.P("Aucune note trouvée", style={
                'color': colors['subtext'],
                'textAlign': 'center',
                'padding': '40px'
            })
        ])
      elif tab == 'tab-4':
        evaluation_data = [
            {'Type': 'Projet', 'Pourcentage': 20, 'Couleur': '#3B82F6'},
            {'Type': 'TP', 'Pourcentage': 10, 'Couleur': '#10B981'},
            {'Type': 'Examen', 'Pourcentage': 70, 'Couleur': '#F59E0B'}
        ]
        return html.Div([
            html.H3("Répartition des évaluations", style={
                'color': colors['text'],
                'marginBottom': '30px',
                'textAlign': 'center'
            }),
            dcc.Graph(
                figure={
                    'data': [{
                        'x': [item['Type'] for item in evaluation_data],
                        'y': [item['Pourcentage'] for item in evaluation_data],
                        'type': 'bar',
                        'marker': {
                            'color': [item['Couleur'] for item in evaluation_data],
                            'line': {'width': 0}
                        },
                        'text': [f"{item['Pourcentage']}%" for item in evaluation_data],
                        'textposition': 'auto',
                        'textfont': {'size': 14, 'color': 'white', 'family': 'Inter, sans-serif'}
                    }],
                    'layout': {
                        'title': {
                            'text': 'Répartition des évaluations (%)',
                            'font': {'size': 18, 'color': colors['text'], 'family': 'Inter, sans-serif'},
                            'x': 0.5
                        },
                        'xaxis': {
                            'title': 'Type d\'évaluation',
                            'titlefont': {'color': colors['text'], 'family': 'Inter, sans-serif'},
                            'tickfont': {'color': colors['text'], 'family': 'Inter, sans-serif'},
                            'gridcolor': '#E2E8F0'
                        },
                        'yaxis': {
                            'title': 'Pourcentage (%)',
                            'titlefont': {'color': colors['text'], 'family': 'Inter, sans-serif'},
                            'tickfont': {'color': colors['text'], 'family': 'Inter, sans-serif'},
                            'gridcolor': '#E2E8F0',
                            'range': [0, 80]
                        },
                        'plot_bgcolor': 'rgba(0,0,0,0)',
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'font': {'family': 'Inter, sans-serif'},
                        'margin': {'l': 60, 'r': 40, 't': 60, 'b': 60}
                    }
                },
                style={'height': '400px', 'marginBottom': '30px'}
            ),
            # Graphique en camembert
            dcc.Graph(
                figure={
                    'data': [{
                        'labels': [item['Type'] for item in evaluation_data],
                        'values': [item['Pourcentage'] for item in evaluation_data],
                        'type': 'pie',
                        'marker': {
                            'colors': [item['Couleur'] for item in evaluation_data],
                            'line': {'width': 2, 'color': 'white'}
                        },
                        'textinfo': 'label+percent',
                        'textfont': {'size': 14, 'color': 'white', 'family': 'Inter, sans-serif'},
                        'hovertemplate': '<b>%{label}</b><br>%{value}%<br><extra></extra>'
                    }],
                    'layout': {
                        'title': {
                            'text': 'Répartition des évaluations (Camembert)',
                            'font': {'size': 18, 'color': colors['text'], 'family': 'Inter, sans-serif'},
                            'x': 0.5
                        },
                        'plot_bgcolor': 'rgba(0,0,0,0)',
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'font': {'family': 'Inter, sans-serif'},
                        'margin': {'l': 20, 'r': 20, 't': 60, 'b': 20},
                        'showlegend': True,
                        'legend': {
                            'font': {'color': colors['text'], 'family': 'Inter, sans-serif'}
                        }
                    }
                },
                style={'height': '400px'}
            ),
            # Tableau récapitulatif
            html.Div([
                html.H4("Détail des coefficients", style={
                    'color': colors['text'],
                    'marginTop': '30px',
                    'marginBottom': '15px'
                }),
                dash_table.DataTable(
                    data=evaluation_data,
                    columns=[
                        {'name': 'Type d\'évaluation', 'id': 'Type'},
                        {'name': 'Pourcentage', 'id': 'Pourcentage', 'type': 'numeric', 'format': {'specifier': '.0f'}}
                    ],
                    style_table={'overflowX': 'auto', 'maxWidth': '400px', 'margin': '0 auto'},
                    style_cell={
                        'textAlign': 'center',
                        'padding': '15px',
                        'fontFamily': 'Inter, sans-serif',
                        'fontSize': '14px',
                        'border': 'none',
                        'borderBottom': '1px solid #E2E8F0'
                    },
                    style_header={
                        'backgroundColor': colors['bg_color'],
                        'fontWeight': '600',
                        'border': 'none',
                        'borderBottom': '2px solid #E2E8F0',
                        'color': colors['text']
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': colors['bg_color']}
                    ]
                )
            ])
        ])
    return html.Div([
        html.P("Onglet non reconnu", style={
            'color': colors['subtext'],
            'textAlign': 'center',
            'padding': '40px'
        })
    ])
premier_etudiant = None
try:
    premier_etudiant = Utilisateur.objects.filter(role='ETU').first()
except:
    try:
        from django.contrib.auth.models import User
        users = Utilisateur.objects.all()
        if users.exists():
            premier_etudiant = users.first()
        else:
            test_user = Utilisateur.objects.create(
                username="etudiant_test",
                first_name="Prénom",
                last_name="Nom",
                email="test@example.com",
                role="ETU"
            )
            premier_etudiant = test_user
    except Exception as e:
        print(f"Erreur lors de la création d'un utilisateur de test: {e}")
