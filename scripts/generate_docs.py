import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_pdf(filename, title, content_blocks):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=54, leftMargin=54,
                            topMargin=54, bottomMargin=54)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=6
    )

    # Document Header
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    
    # Divider line
    divider = Table([['']], colWidths=[504])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor('#1A365D')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))
    
    # Add Content
    for block in content_blocks:
        block_type = block.get('type', 'p')
        text = block.get('text', '')
        
        if block_type == 'h2':
            story.append(Paragraph(text, h2_style))
        elif block_type == 'p':
            story.append(Paragraph(text, body_style))
        elif block_type == 'bullet':
            story.append(Paragraph(f"&bull; {text}", bullet_style))
        elif block_type == 'spacer':
            story.append(Spacer(1, block.get('height', 10)))
        elif block_type == 'table':
            data = block.get('data', [])
            # Format table content as paragraphs to wrap text properly
            formatted_data = []
            for row in data:
                formatted_row = []
                for cell in row:
                    if isinstance(cell, str):
                        formatted_row.append(Paragraph(cell, body_style))
                    else:
                        formatted_row.append(cell)
                formatted_data.append(formatted_row)
            
            col_widths = block.get('col_widths', None)
            t = Table(formatted_data, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ]))
            story.append(t)
            story.append(Spacer(1, 10))
            
    doc.build(story)
    print(f"Document généré : {filename}")

def main():
    # PDF 1 : Règlement Intérieur
    reglement_content = [
        {'type': 'h2', 'text': '1. Horaires et Accès au Campus'},
        {'type': 'p', 'text': "Le campus de l'école est accessible du lundi au vendredi de 8h30 à 18h30. Les cours officiels commencent à 9h00 précises et se terminent à 17h00. Les étudiants doivent badger à l'entrée du bâtiment pour des raisons de sécurité."},
        
        {'type': 'h2', 'text': '2. Gestion des Absences'},
        {'type': 'bullet', 'text': "<b>Délai de justification :</b> Toute absence à un cours doit être obligatoirement signalée et justifiée auprès du secrétariat pédagogique dans un délai maximum de 48 heures."},
        {'type': 'bullet', 'text': "<b>Justificatifs acceptés :</b> Seuls les certificats médicaux, convocations officielles ou attestations d'employeur (pour les alternants) sont acceptés comme justificatifs valables."},
        {'type': 'bullet', 'text': "<b>Absences injustifiées :</b> Au-delà de 3 absences injustifiées au cours du semestre, l'étudiant sera convoqué devant la commission de discipline, ce qui peut mener à une exclusion temporaire ou définitive."},
        
        {'type': 'h2', 'text': '3. Règles de Vie et Sécurité'},
        {'type': 'bullet', 'text': "<b>Salles informatiques :</b> Il est strictement interdit de manger ou de boire dans les salles informatiques afin de protéger le matériel informatique."},
        {'type': 'bullet', 'text': "<b>Respect du matériel :</b> Tout dommage causé volontairement au matériel de l'école sera facturé à l'étudiant concerné."},
        
        {'type': 'h2', 'text': '4. Intégrité Académique et Examens'},
        {'type': 'p', 'text': "Le plagiat, la triche ou l'utilisation non autorisée de documents ou de téléphones pendant les examens et les rendus de projets sont strictement interdits. Toute fraude constatée sera immédiatement sanctionnée par la note de 0/20 pour le module concerné, accompagnée d'un passage automatique devant le conseil de discipline de l'école."},
    ]
    create_pdf('docs/reglement_interieur.pdf', 'Règlement Intérieur de l\'École', reglement_content)

    # PDF 2 : Syllabus des Cours
    syllabus_content = [
        {'type': 'p', 'text': "Ce document présente le syllabus détaillé des modules de formation pour le semestre en cours."},
        
        {'type': 'h2', 'text': 'Module 1 : Python et Data Science'},
        {'type': 'bullet', 'text': "<b>Volume horaire :</b> 30 heures de cours et travaux pratiques."},
        {'type': 'bullet', 'text': "<b>Crédits :</b> 4 ECTS."},
        {'type': 'bullet', 'text': "<b>Intervenant :</b> Dr. Jean Dupont (jean.dupont@ecole.fr)."},
        {'type': 'bullet', 'text': "<b>Évaluation :</b> 1 projet de groupe (50% de la note finale) et 1 examen individuel écrit sur table (50% de la note finale)."},
        
        {'type': 'h2', 'text': 'Module 2 : Intelligence Artificielle et RAG (Retrieval-Augmented Generation)'},
        {'type': 'bullet', 'text': "<b>Volume horaire :</b> 20 heures de cours et ateliers pratiques."},
        {'type': 'bullet', 'text': "<b>Crédits :</b> 3 ECTS."},
        {'type': 'bullet', 'text': "<b>Intervenante :</b> Mme. Alice Martin (alice.martin@ecole.fr)."},
        {'type': 'bullet', 'text': "<b>Évaluation :</b> 1 projet pratique individuel consistant à développer une application RAG complète (100% de la note)."},
        
        {'type': 'h2', 'text': 'Module 3 : Business Stratégie et ROI des Projets IA'},
        {'type': 'bullet', 'text': "<b>Volume horaire :</b> 25 heures."},
        {'type': 'bullet', 'text': "<b>Crédits :</b> 3 ECTS."},
        {'type': 'bullet', 'text': "<b>Intervenant :</b> M. Robert Durand (robert.durand@ecole.fr)."},
        {'type': 'bullet', 'text': "<b>Évaluation :</b> 1 étude de cas business en groupe présentée à l'oral (100% de la note)."},
        
        {'type': 'h2', 'text': 'Règles de rendu des projets'},
        {'type': 'p', 'text': "Tous les projets doivent être obligatoirement déposés sur la plateforme d'apprentissage en ligne de l'école (LMS) avant le dimanche soir 23h59 de la semaine indiquée dans le calendrier de rendu. Tout retard de rendu sans accord préalable écrit de l'intervenant entraînera une pénalité systématique de 2 points par jour de retard sur la note finale du projet."},
    ]
    create_pdf('docs/syllabus_cours.pdf', 'Syllabus des Modules et Évaluations', syllabus_content)

    # PDF 3 : Informations Pratiques & Contacts
    pratiques_content = [
        {'type': 'p', 'text': "Ce document contient toutes les informations pratiques relatives au fonctionnement du campus, aux examens et aux contacts administratifs."},
        
        {'type': 'h2', 'text': '1. Calendrier des Examens'},
        {'type': 'table', 'data': [
            ['Événement', 'Dates', 'Description'],
            ['Session d\'examens Semestre 2', 'Du 15 au 19 juin 2026', 'Examens écrits sur table et soutenances de projets de fin de semestre.'],
            ['Session de rattrapage', 'Du 7 au 11 septembre 2026', 'Rattrapages pour les modules non validés (note inférieure à 10/20).']
        ], 'col_widths': [120, 120, 264]},
        
        {'type': 'h2', 'text': '2. Contacts Administratifs et Pédagogiques'},
        {'type': 'table', 'data': [
            ['Service', 'Contact Email', 'Rôle / Responsabilités'],
            ['Secrétariat Pédagogique', 'secretariat@ecole.fr', 'Gestion des absences, inscriptions, relevés de notes. Tel: 01 23 45 67 89'],
            ['Support Informatique', 'support@ecole.fr', 'Problèmes de WIFI, création de comptes, accès aux salles de TP.'],
            ['Responsable des Stages', 'stages@ecole.fr', 'Accompagnement dans la recherche de stage ou de contrat d\'alternance.'],
            ['Responsable des Programmes', 'responsable@ecole.fr', 'Réclamations pédagogiques, choix d\'options, réorientations.']
        ], 'col_widths': [130, 150, 224]},
        
        {'type': 'h2', 'text': '3. Accès au Réseau et WiFi'},
        {'type': 'p', 'text': "Le réseau WiFi destiné aux étudiants s'appelle <b>EDUPSTB-GUEST</b>. Le mot de passe de connexion est <b>Pstb2026!</b>. Il est strictement interdit d'utiliser des routeurs personnels ou de modifier la configuration réseau des ordinateurs des salles de TP."},
    ]
    create_pdf('docs/infos_pratiques.pdf', 'Informations Pratiques, WiFi et Contacts', pratiques_content)

    # PDF 4 : Organisation Générale et Objectifs des Modules
    organisation_content = [
        {'type': 'p', 'text': "Ce document détaille l'organisation de la formation, ainsi que les objectifs d'apprentissage de chaque module."},
        
        {'type': 'h2', 'text': '1. Objectifs d\'Apprentissage des Modules'},
        {'type': 'bullet', 'text': "<b>Module Python et Data Science :</b> Maîtriser le nettoyage, la manipulation et la visualisation de données avec Pandas et Numpy. Apprendre à concevoir des modèles d'apprentissage automatique supervisés."},
        {'type': 'bullet', 'text': "<b>Module Intelligence Artificielle et RAG :</b> Comprendre le fonctionnement des grands modèles de langage (LLMs), concevoir des pipelines de RAG en local, et maîtriser le stockage vectoriel dans ChromaDB."},
        {'type': 'bullet', 'text': "<b>Module Business Stratégie et ROI :</b> Apprendre à évaluer l'impact financier d'un projet d'IA, calculer son Retour sur Investissement (ROI), et formaliser un business case solide."},
        
        {'type': 'h2', 'text': '2. Organisation Générale de la Formation'},
        {'type': 'p', 'text': "La formation est organisée sur deux semestres académiques combinant cours magistraux, travaux pratiques (TP) et projets de groupe. Le passage en année supérieure nécessite la validation de l'ensemble des modules (moyenne supérieure ou égale à 10/20) et la validation de la période obligatoire d'immersion professionnelle."},
        {'type': 'bullet', 'text': "<b>Période professionnelle :</b> Un stage obligatoire ou un contrat d'alternance d'une durée minimale de 4 mois débute à partir du 1er juillet."},
        
        {'type': 'h2', 'text': '3. Règlement de Retard'},
        {'type': 'bullet', 'text': "<b>Retard supérieur à 15 minutes :</b> Tout étudiant arrivant avec un retard de plus de 15 minutes après le début officiel du cours se verra refuser l'entrée en classe pour la demi-journée. Il sera marqué absent de manière injustifiée."},
        {'type': 'bullet', 'text': "<b>Retards répétés :</b> Deux retards inférieurs à 15 minutes au cours d'un même mois sont comptabilisés comme une absence injustifiée."},
    ]
    create_pdf('docs/organisation_formation.pdf', 'Organisation Générale et Objectifs de la Formation', organisation_content)

if __name__ == '__main__':
    main()
