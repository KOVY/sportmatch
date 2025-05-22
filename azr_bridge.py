"""
AZR Bridge - Python část pro Absolute Zero Reasoner

Tento skript slouží jako most mezi Node.js aplikací a Python kódem,
který poskytuje lokální AI modely a další funkce pro AZR.
"""

import sys
import json
import time
from typing import Dict, Any, List, Optional, Union

# Pokus o import pokročilých modulů
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Přehled funkcí poskytovaných AZR modulem
MODULE_CAPABILITIES = {
    "basic_analysis": True,
    "vectorization": HAS_NUMPY and HAS_SKLEARN,
    "data_processing": HAS_PANDAS,
    "local_models": HAS_TRANSFORMERS and HAS_TORCH,
    "version": "0.1.0"
}

# Třída pro zpracování AZR dotazů
class AZRProcessor:
    def __init__(self):
        self.models = {}
        self.cache = {}
        
    def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zpracování AZR dotazu
        """
        query_type = query.get("type", "unknown")
        data = query.get("data", {})
        options = query.get("options", {})
        
        # Logování
        print(f"Zpracování dotazu typu: {query_type}", file=sys.stderr)
        
        try:
            # Výběr procesoru podle typu dotazu
            if query_type == "reservation_analysis":
                result = self.process_reservation_analysis(data, options)
            elif query_type == "conflict_resolution":
                result = self.process_conflict_resolution(data, options)
            elif query_type == "user_reservation_analysis":
                result = self.process_user_reservation_analysis(data, options)
            elif query_type == "token_analysis":
                result = self.process_token_analysis(data, options)
            elif query_type == "text_vectorization":
                result = self.process_text_vectorization(data, options)
            elif query_type == "azr_capabilities":
                result = self.get_capabilities()
            elif query_type == "analysis" or query_type == "app_analysis":
                # Nový typ dotazu pro analýzu aplikace
                query_text = query.get("query", "")
                if query_text:
                    result = self.process_app_analysis(query_text, options)
                else:
                    result = {"error": "Dotaz pro analýzu aplikace musí obsahovat 'query' s textem dotazu"}
            else:
                # Neznámý typ dotazu
                result = {"error": f"Neznámý typ dotazu: {query_type}",
                          "dostupne_typy": ["reservation_analysis", "conflict_resolution", 
                                            "user_reservation_analysis", "token_analysis",
                                            "text_vectorization", "azr_capabilities", 
                                            "analysis", "app_analysis"]}
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            else:
                return {"success": True, "data": result}
            
        except Exception as e:
            # Zachycení případných chyb
            import traceback
            error_traceback = traceback.format_exc()
            return {
                "success": False, 
                "error": f"Chyba při zpracování dotazu: {str(e)}",
                "traceback": error_traceback
            }
    
    def process_reservation_analysis(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zpracování analýzy rezervace
        """
        suggestion = data.get("suggestion", {})
        request = data.get("request", {})
        
        # Základní analýza návrhu rezervace
        enhanced_suggestion = {
            "additionalReasons": []
        }
        
        # Analýza času
        start_time = suggestion.get("startTime", "")
        if start_time:
            hour = int(start_time.split(":")[0])
            if 8 <= hour <= 10:
                enhanced_suggestion["additionalReasons"].append(
                    "Ranní hodiny jsou obvykle méně vytížené, což zvyšuje kvalitu vašeho zážitku."
                )
            elif 17 <= hour <= 20:
                enhanced_suggestion["additionalReasons"].append(
                    "Večerní hodiny jsou obvykle více vytížené, což může ovlivnit dostupnost zařízení a šaten."
                )
        
        # Analýza dne v týdnu
        date = suggestion.get("date", "")
        if date:
            day_names = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]
            if "sobota" in date.lower() or "neděle" in date.lower() or any(day in date.lower() for day in ["so", "ne"]):
                enhanced_suggestion["additionalReasons"].append(
                    "Víkendy jsou obvykle více vytížené, ale nabízejí příjemnější atmosféru pro rekreační sportovce."
                )
        
        # Analýza ceny
        price = suggestion.get("price", 0)
        token_price = suggestion.get("tokenPrice", 0)
        if price and token_price:
            if token_price <= 5:
                enhanced_suggestion["additionalReasons"].append(
                    f"Platba FitnessTokeny je v tomto případě výhodná, ušetříte až {int(price * 0.15)} Kč oproti standardní ceně."
                )
        
        # Vrácení výsledku
        return {"enhancedSuggestion": enhanced_suggestion}
    
    def process_conflict_resolution(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zpracování řešení konfliktu
        """
        conflict = data.get("conflict", {})
        reservation1 = data.get("reservation1", {})
        reservation2 = data.get("reservation2", {})
        
        # Základní analýza konfliktu
        resolution = "Na základě analýzy doporučuji následující řešení konfliktu:"
        
        # Porovnání rezervací
        suggestions = []
        
        # Příklad: podle typu rezervace
        if reservation1.get("type") == "facility" and reservation2.get("type") == "tournament":
            resolution += "\nTurnajová rezervace by měla mít přednost před individuální rezervací sportoviště."
            suggestions.append({
                "title": "Přesunutí individuální rezervace",
                "description": "Přesunout individuální rezervaci na jiný volný termín a potvrdit turnaj.",
                "priority": "high"
            })
        else:
            # Obecné doporučení
            resolution += "\nDoporučuji analyzovat prioritu rezervací podle počtu účastníků a typu aktivity."
            suggestions.append({
                "title": "Konzultace s oběma stranami",
                "description": "Kontaktovat obě strany a najít kompromisní řešení.",
                "priority": "medium"
            })
        
        # Vrácení výsledku
        return {
            "resolution": resolution,
            "suggestions": suggestions
        }
    
    def process_user_reservation_analysis(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zpracování analýzy rezervací uživatele
        """
        user_id = data.get("userId", 0)
        reservations = data.get("reservations", [])
        
        if not reservations:
            return {
                "summary": "Zatím nemáte žádné rezervace.",
                "insights": ["Vytvořte svou první rezervaci a získejte personalizovaná doporučení."],
                "recommendations": []
            }
        
        # Základní analýza historie rezervací
        summary = f"Analýza {len(reservations)} rezervací"
        insights = []
        recommendations = []
        
        # Počítání typů rezervací
        reservation_types = {}
        for res in reservations:
            res_type = res.get("type", "unknown")
            reservation_types[res_type] = reservation_types.get(res_type, 0) + 1
        
        # Přidání insights podle typů
        for res_type, count in reservation_types.items():
            type_name = {
                "facility": "sportoviště",
                "trainer": "trenér",
                "tournament": "turnaj"
            }.get(res_type, res_type)
            
            insights.append(f"Máte {count} rezervací typu {type_name}.")
            
            # Doporučení podle typu
            if res_type == "facility" and count >= 3:
                recommendations.append({
                    "title": "Zvažte FitnessTokens",
                    "description": "Při vaší frekvenci rezervací sportovišť by bylo výhodné využít FitnessTokens pro slevu až 20%."
                })
            elif res_type == "trainer" and count >= 2:
                recommendations.append({
                    "title": "Dlouhodobá spolupráce s trenérem",
                    "description": "Zvažte pravidelné tréninky s trenérem pro lepší ceny a konzistentní pokrok."
                })
        
        # Vrácení výsledku
        return {
            "summary": summary,
            "insights": insights,
            "recommendations": recommendations
        }
    
    def process_token_analysis(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zpracování analýzy FitnessTokens - pokročilá analýza transakcí a generování doporučení
        """
        user_id = data.get("userId", "")
        transactions = data.get("transactions", [])
        timeframe = options.get("timeframe", "month")
        prediction_window = options.get("predictionWindow", "month")
        
        if not HAS_PANDAS:
            return {"error": "Modul pandas není k dispozici pro analýzu tokenů."}
        
        if not transactions:
            return {
                "summary": {
                    "totalEarned": 0,
                    "totalSpent": 0,
                    "netChange": 0,
                    "averageTransaction": 0,
                    "transactionCount": 0,
                    "highestSingleTransaction": 0
                },
                "patterns": {
                    "weekdayDistribution": {},
                    "hourlyDistribution": {},
                    "categoryDistribution": {},
                    "monthlyTrend": []
                },
                "predictions": {
                    "estimatedNextMonthEarnings": 0,
                    "estimatedNextMonthSpendings": 0,
                    "predictedBalance": 0,
                    "savingPotential": 0,
                    "earningOpportunities": []
                },
                "recommendations": {
                    "general": [],
                    "personalized": []
                }
            }
        
        # Konverze na pandas DataFrame pro analýzu
        try:
            df = pd.DataFrame(transactions)
            
            # Konverze transactionDate na datetime
            df['transactionDate'] = pd.to_datetime(df['transactionDate'])
            
            # Rozšíření dat o časové informace
            df['day'] = df['transactionDate'].dt.day_name()
            df['hour'] = df['transactionDate'].dt.hour
            df['month'] = df['transactionDate'].dt.strftime('%Y-%m')
            df['week'] = df['transactionDate'].dt.strftime('%Y-%W')
            
            # Základní výpočty
            total_earned = df[df['type'] == 'earned']['amount'].sum()
            total_spent = df[df['type'] == 'spent']['amount'].sum()
            
            # Identifikace oblíbených kategorií
            if 'category' in df.columns and not df['category'].isna().all():
                earning_categories = df[df['type'] == 'earned'].groupby('category')['amount'].sum()
                spending_categories = df[df['type'] == 'spent'].groupby('category')['amount'].sum()
                
                favorite_earning_category = earning_categories.idxmax() if not earning_categories.empty else None
                favorite_spending_category = spending_categories.idxmax() if not spending_categories.empty else None
            else:
                favorite_earning_category = None
                favorite_spending_category = None
            
            # Identifikace posledního data transakce
            most_recent_transaction = df['transactionDate'].max() if not df.empty else None
            
            # Vytvoření výsledků analýzy
            summary = {
                "totalEarned": float(total_earned),
                "totalSpent": float(total_spent),
                "netChange": float(total_earned - total_spent),
                "averageTransaction": float(df['amount'].mean()),
                "transactionCount": len(df),
                "favoriteEarningCategory": favorite_earning_category,
                "favoriteSpendingCategory": favorite_spending_category,
                "highestSingleTransaction": float(df['amount'].max()),
                "mostRecentTransaction": most_recent_transaction.isoformat() if most_recent_transaction else None
            }
            
            # Analýza vzorů
            weekday_distribution = df.groupby('day')['amount'].sum().to_dict()
            hourly_distribution = df.groupby('hour')['amount'].sum().to_dict()
            
            if 'category' in df.columns and not df['category'].isna().all():
                category_distribution = df.groupby('category')['amount'].sum().to_dict()
            else:
                category_distribution = {"Uncategorized": float(df['amount'].sum())}
            
            # Měsíční trendy
            monthly_trend = []
            for month, group in df.groupby('month'):
                monthly_trend.append({
                    "month": month,
                    "earned": float(group[group['type'] == 'earned']['amount'].sum()),
                    "spent": float(group[group['type'] == 'spent']['amount'].sum())
                })
            
            # Seřazení podle měsíce
            monthly_trend.sort(key=lambda x: x['month'])
            
            patterns = {
                "weekdayDistribution": {k: float(v) for k, v in weekday_distribution.items()},
                "hourlyDistribution": {str(k): float(v) for k, v in hourly_distribution.items()},
                "categoryDistribution": {k: float(v) for k, v in category_distribution.items()},
                "monthlyTrend": monthly_trend
            }
            
            # Predikce budoucího využití
            # Jednoduchý lineární model pro predikci
            if len(monthly_trend) > 1:
                recent_months = monthly_trend[-3:] if len(monthly_trend) >= 3 else monthly_trend
                avg_earned = sum(m['earned'] for m in recent_months) / len(recent_months)
                avg_spent = sum(m['spent'] for m in recent_months) / len(recent_months)
                
                # Aplikace trendu (mírný růst příjmů, stabilizace výdajů)
                growth_factor = 1.05  # 5% nárůst pro příjmy
                estimated_next_month_earnings = avg_earned * growth_factor
                estimated_next_month_spendings = avg_spent * 0.95  # 5% úspora
                
                predicted_balance = float(total_earned - total_spent) + (estimated_next_month_earnings - estimated_next_month_spendings)
                saving_potential = avg_spent * 0.15  # 15% potenciál úspory
            else:
                # Pokud nemáme dostatek dat, použijeme základní odhad
                estimated_next_month_earnings = total_earned * 0.1 if total_earned > 0 else 10
                estimated_next_month_spendings = total_spent * 0.1 if total_spent > 0 else 5
                predicted_balance = float(total_earned - total_spent) * 1.05  # Mírný nárůst
                saving_potential = total_spent * 0.15 if total_spent > 0 else 2
            
            # Identifikace příležitostí pro získání tokenů
            earning_opportunities = []
            
            if 'category' in df.columns and not df['category'].isna().all():
                # Analýza nevyužitých kategorií nebo kategorií s nízkým zastoupením
                all_categories = set(['sports', 'challenges', 'rewards', 'reservations', 'events', 'transfers', 'purchases'])
                used_categories = set(df['category'].dropna().unique())
                unused_categories = all_categories - used_categories
                
                for category in unused_categories:
                    earning_opportunities.append({
                        "type": category.capitalize(),
                        "potential": float(20),  # Základní potenciál
                        "confidence": 0.8,
                        "description": f"Začněte využívat možnosti v kategorii {category} pro získání dalších tokenů."
                    })
            
            # Přidání dalších příležitostí
            earning_opportunities.append({
                "type": "Weekly Challenge",
                "potential": float(25),
                "confidence": 0.85,
                "description": "Účastněte se týdenní výzvy pro získání až 25 tokenů."
            })
            
            if total_spent > total_earned:
                earning_opportunities.append({
                    "type": "Balance Improvement",
                    "potential": float(total_spent - total_earned),
                    "confidence": 0.7,
                    "description": "Zaměřte se na vyrovnání příjmů a výdajů pomocí pravidelných aktivit."
                })
            
            predictions = {
                "estimatedNextMonthEarnings": float(estimated_next_month_earnings),
                "estimatedNextMonthSpendings": float(estimated_next_month_spendings),
                "predictedBalance": float(predicted_balance),
                "savingPotential": float(saving_potential),
                "earningOpportunities": earning_opportunities
            }
            
            # Generování doporučení
            general_recommendations = []
            personalized_recommendations = []
            
            # Základní doporučení pro všechny uživatele
            general_recommendations.append({
                "type": "activity",
                "title": "Pravidelné sportovní aktivity",
                "description": "Účastněte se alespoň 2 sportovních aktivit týdně pro konstantní přísun tokenů.",
                "impact": "medium",
                "actionable": True
            })
            
            general_recommendations.append({
                "type": "challenge",
                "title": "Výzvy a soutěže",
                "description": "Zapojte se do měsíčních výzev, které mohou významně zvýšit váš zůstatek tokenů.",
                "impact": "high",
                "actionable": True
            })
            
            # Personalizovaná doporučení
            if total_spent > total_earned * 1.5:
                personalized_recommendations.append({
                    "type": "savings",
                    "title": "Optimalizujte své výdaje",
                    "description": "Vaše výdaje převyšují příjmy. Zvažte rezervaci sportovišť v méně vytížených hodinách pro nižší ceny.",
                    "impact": "high",
                    "relevanceScore": 0.9
                })
            
            if 'category' in df.columns and not df['category'].isna().all():
                # Analýza nejúspěšnějších kategorií pro uživatele
                if favorite_earning_category:
                    personalized_recommendations.append({
                        "type": favorite_earning_category.lower(),
                        "title": f"Maximalizujte zisky v {favorite_earning_category}",
                        "description": f"Tato kategorie vám přináší nejvíce tokenů. Zaměřte se na další aktivity v kategorii {favorite_earning_category}.",
                        "impact": "medium",
                        "relevanceScore": 0.8
                    })
            
            # Doporučení na základě času aktivit
            if 'hour' in df.columns:
                active_hours = df.groupby('hour')['amount'].sum().sort_values(ascending=False).index[:3].tolist()
                if active_hours:
                    hour_str = ", ".join([f"{h}:00" for h in active_hours])
                    personalized_recommendations.append({
                        "type": "timing",
                        "title": "Optimální čas pro vaše aktivity",
                        "description": f"Vaše nejproduktivnější hodiny jsou kolem {hour_str}. Plánujte své aktivity v těchto časech pro maximální efektivitu.",
                        "impact": "low",
                        "relevanceScore": 0.7
                    })
            
            recommendations = {
                "general": general_recommendations,
                "personalized": personalized_recommendations
            }
            
            return {
                "summary": summary,
                "patterns": patterns,
                "predictions": predictions,
                "recommendations": recommendations
            }
            
        except Exception as e:
            return {
                "error": f"Chyba při analýze tokenů: {str(e)}",
                "summary": {
                    "totalEarned": 0,
                    "totalSpent": 0,
                    "netChange": 0,
                    "averageTransaction": 0,
                    "transactionCount": len(transactions),
                    "highestSingleTransaction": 0
                },
                "patterns": {
                    "weekdayDistribution": {},
                    "hourlyDistribution": {},
                    "categoryDistribution": {},
                    "monthlyTrend": []
                },
                "predictions": {
                    "estimatedNextMonthEarnings": 0,
                    "estimatedNextMonthSpendings": 0,
                    "predictedBalance": 0,
                    "savingPotential": 0,
                    "earningOpportunities": []
                },
                "recommendations": {
                    "general": [],
                    "personalized": []
                }
            }
        
        if statistics["transactionCount"] > 5:
            recommendations.append({
                "title": "Optimalizujte své výdaje",
                "description": "Naplánujte si aktivity dopředu a využívejte rezervace v době mimo špičku pro úsporu tokenů."
            })
            
        # Vrácení výsledku
        return {
            "summary": f"Celková bilance: {total_tokens} tokenů (utraceno: {total_spent}, získáno: {total_earned})",
            "statistics": statistics,
            "recommendations": recommendations
        }
    
    def process_text_vectorization(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vektorizace textu a podobnostní analýza
        """
        if not (HAS_NUMPY and HAS_SKLEARN):
            return {"error": "Moduly sklearn a numpy nejsou k dispozici pro textovou analýzu."}
        
        texts = data.get("texts", [])
        query = data.get("query", "")
        
        if not texts:
            return {"error": "Žádné texty k analýze."}
        
        if not query:
            return {"error": "Žádný dotaz pro porovnání."}
        
        # Vektorizace textů
        tfidf = TfidfVectorizer()
        all_texts = texts + [query]
        tfidf_matrix = tfidf.fit_transform(all_texts)
        
        # Výpočet podobnosti
        query_vector = tfidf_matrix[-1]
        document_vectors = tfidf_matrix[:-1]
        
        # Podobnost mezi dotazem a dokumenty
        similarities = cosine_similarity(query_vector, document_vectors)[0]
        
        # Seřazení výsledků podle podobnosti
        ranked_results = [
            {"index": idx, "text": texts[idx], "similarity": float(sim)} 
            for idx, sim in enumerate(similarities)
        ]
        ranked_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Vrácení výsledku
        return {
            "results": ranked_results,
            "topResult": ranked_results[0] if ranked_results else None,
            "featuresAnalyzed": len(tfidf.get_feature_names_out())
        }
    
    def process_app_analysis(self, query_text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zpracování analýzy aplikace na základě textového dotazu
        
        Tato metoda posoudí stav aplikace, její výhody a nevýhody, a poskytne
        doporučení pro další vývoj. Využívá informace z různých částí systému.
        """
        # Zpracování dotazu
        detailed = options.get("detailed", False)
        include_rationale = options.get("include_rationale", False)
        
        # Základní analýza aplikace
        try:
            # Import a volání skriptu pro analýzu
            import subprocess
            import json
            
            # Spustíme skript pro analýzu aplikace
            result = subprocess.run(
                ["python3", "app_analysis.py"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Parsování výstupu
            analysis_data = json.loads(result.stdout)
            
            # Příprava odpovědi
            response = {
                "title": "Analýza aplikace SportMatch",
                "timestamp": analysis_data.get("timestamp"),
                "summary": analysis_data.get("summary", ""),
                "strengths": analysis_data.get("strengths", []),
                "recommendations": analysis_data.get("recommendations", []),
                "query_context": {
                    "query": query_text,
                    "detailed": detailed,
                    "include_rationale": include_rationale
                }
            }
            
            # Přidání podrobné zprávy, pokud je vyžádána
            if detailed:
                metrics = {
                    "czech_pages_count": analysis_data.get("structure", {}).get("czech_pages_count", 0),
                    "english_pages_count": analysis_data.get("structure", {}).get("english_pages_count", 0),
                    "components_count": analysis_data.get("structure", {}).get("components_count", 0),
                    "coverage_ratio": analysis_data.get("structure", {}).get("czech_pages_count", 0) / 
                                     max(1, analysis_data.get("structure", {}).get("english_pages_count", 1))
                }
                response["metrics"] = metrics
            
            # Interpretace dotazu a příprava kontextové odpovědi
            if "české verze" in query_text.lower() or "lokalizace" in query_text.lower():
                response["contextual_answer"] = self._analyze_localization(analysis_data)
            elif "uživatelský zážitek" in query_text.lower() or "ui" in query_text.lower():
                response["contextual_answer"] = self._analyze_user_experience(analysis_data)
            else:
                response["contextual_answer"] = "Analýza celkového stavu aplikace SportMatch ukazuje, že " + \
                                              f"aplikace má {len(analysis_data.get('strengths', []))} silných stránek a " + \
                                              f"{len(analysis_data.get('recommendations', []))} doporučení pro zlepšení."
            
            return response
            
        except Exception as e:
            # Záložní odpověď v případě selhání analýzy
            return {
                "title": "Zjednodušená analýza aplikace SportMatch",
                "summary": "Podrobná analýza nebyla možná kvůli technickým problémům.",
                "error": str(e),
                "recommendations": [
                    {"title": "Rozšířit českou lokalizaci", 
                     "description": "Dokončit překlad všech stránek do češtiny."},
                    {"title": "Optimalizace načítání obrázků",
                     "description": "Implementovat lazy loading a placeholdery pro všechny obrázky v aplikaci."},
                    {"title": "Zlepšit zpracování chyb",
                     "description": "Přidat více informativní chybové hlášky pro lepší diagnostiku problémů."}
                ]
            }
    
    def _analyze_localization(self, analysis_data: Dict[str, Any]) -> str:
        """Pomocná metoda pro analýzu stavu lokalizace"""
        czech_pages = analysis_data.get("structure", {}).get("czech_pages_count", 0)
        english_pages = analysis_data.get("structure", {}).get("english_pages_count", 0)
        
        if czech_pages >= english_pages * 0.9:
            return "Česká lokalizace je na velmi dobré úrovni, pokrývá většinu obsahu aplikace."
        elif czech_pages >= english_pages * 0.7:
            return "Česká lokalizace je na dobré cestě, ale stále chybí přeložit některé stránky."
        else:
            return "Česká lokalizace má značné mezery, je třeba dokončit překlad většího množství stránek."
    
    def _analyze_user_experience(self, analysis_data: Dict[str, Any]) -> str:
        """Pomocná metoda pro analýzu uživatelského zážitku"""
        design_system_usage = analysis_data.get("ui", {}).get("design_system_usage", 0)
        
        if design_system_usage >= 30:
            return "Uživatelské rozhraní aplikace je konzistentní, využívá designový systém ve většině komponent."
        elif design_system_usage >= 15:
            return "Designový systém je částečně implementován, ale některé části UI nejsou zcela konzistentní."
        else:
            return "Uživatelské rozhraní není konzistentní, je třeba více používat komponenty z designového systému."
            
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Získání schopností AZR modulu
        """
        return MODULE_CAPABILITIES

def main():
    """
    Hlavní funkce zpracovávající AZR dotaz z Node.js
    """
    # Kontrola parametrů
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Nesprávný počet parametrů. Očekává se: python azr_bridge.py <query_json>"
        }))
        sys.exit(1)
    
    # Načtení dotazu
    try:
        query_json = sys.argv[1]
        query = json.loads(query_json)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Neplatný JSON: {str(e)}"
        }))
        sys.exit(1)
    
    # Zpracování dotazu
    processor = AZRProcessor()
    result = processor.process_query(query)
    
    # Výstup výsledku
    print(json.dumps(result))

if __name__ == "__main__":
    main()