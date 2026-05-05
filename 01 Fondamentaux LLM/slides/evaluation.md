## 1. BLEU (Bilingual Evaluation Understudy) — pour la traduction

**À quoi ça sert :** Évaluer la qualité d'une traduction automatique en la comparant à une (ou plusieurs) traduction(s) de référence faite par des humains.

**Principe :** Mesure la **précision** sur les n-grammes (séquences de n mots consécutifs). On regarde combien de n-grammes générés par la machine apparaissent aussi dans la référence.

**La formule décortiquée :**

$$BLEU = BP \cdot \exp\left(\sum_{n=1}^{N} w_n \log p_n\right)$$

- **pₙ** : précision pour les n-grammes de taille n. Par exemple, p₁ = unigrammes, p₂ = bigrammes, etc. On compte combien de n-grammes du candidat sont présents dans la référence, divisé par le nombre total de n-grammes du candidat.
- **wₙ = 1/N** : poids uniforme pour chaque taille de n-gramme (typiquement N=4, donc on moyenne sur n=1,2,3,4).
- **La somme des log** : c'est une moyenne géométrique des précisions (passer en log permet de transformer le produit en somme).
- **BP (Brevity Penalty)** : pénalité de brièveté. Si le candidat est plus court que la référence, on le pénalise pour éviter qu'un système triche en produisant des sorties très courtes mais "précises".
  - BP = min(1, e^(1−r/c)) où r = longueur de la référence, c = longueur du candidat.
  - Si c ≥ r → BP = 1 (pas de pénalité). Si c < r → BP < 1 (pénalité).

**Plage de valeurs :** entre 0 et 1 (souvent exprimée en %). Plus c'est haut, mieux c'est.

**Limites :** ne capture pas le sens, juste la correspondance lexicale. Une bonne traduction utilisant des synonymes peut avoir un BLEU faible.

---

## 2. ROUGE-N (Recall-Oriented Understudy for Gisting Evaluation) — pour le résumé

**À quoi ça sert :** Évaluer la qualité d'un résumé automatique en le comparant à un résumé de référence.

**Principe :** Contrairement à BLEU qui mesure la précision, ROUGE mesure le **rappel (recall)** : combien de n-grammes de la référence ont été retrouvés dans le résumé généré.

**La formule :**

$$ROUGE\text{-}N = \frac{\sum Count_{match}(n\text{-gr})}{\sum Count(n\text{-gr})}$$

- **Numérateur** : nombre de n-grammes qui apparaissent à la fois dans le candidat et dans la référence.
- **Dénominateur** : nombre total de n-grammes dans la référence.

C'est donc une fraction : "quelle proportion du contenu de référence a été couverte par mon résumé ?"

**Les variantes principales :**
- **ROUGE-1** : sur les unigrammes (mots seuls) — mesure le recouvrement de vocabulaire.
- **ROUGE-2** : sur les bigrammes (paires de mots) — mesure la fluidité et la cohérence locale.
- **ROUGE-L** : basée sur la **LCS** (Longest Common Subsequence, plus longue sous-séquence commune). Capture la structure de la phrase sans exiger que les mots soient consécutifs.

**Pourquoi le recall pour les résumés ?** Parce que pour un résumé, ce qui compte c'est de ne pas oublier les infos importantes de la référence. Pour la traduction (BLEU), on veut que ce qui est produit soit correct (précision).

**Limites :** comme BLEU, ROUGE est purement lexical et ne comprend pas le sens.

---

## 3. Perplexité (PPL) — qualité intrinsèque d'un modèle de langage

**À quoi ça sert :** Évaluer un modèle de langage **sans avoir besoin de référence**. C'est une mesure intrinsèque qui dit : à quel point le modèle est-il "surpris" par un texte ?

**La formule :**

$$PPL = \exp\left(-\frac{1}{N} \sum_i \log P(w_i \mid w_{<i})\right)$$

- **P(wᵢ | w<ᵢ)** : probabilité que le modèle attribue au mot wᵢ étant donné tous les mots précédents (w<ᵢ).
- **Somme des log** : on prend le log de chaque probabilité, on les somme.
- **−(1/N) × somme** : c'est l'opposé de la log-vraisemblance moyenne (ou entropie croisée moyenne par mot).
- **exp(...)** : on exponentiate pour ramener ça à une échelle interprétable.

**Interprétation intuitive :** PPL = 50 signifie que, en moyenne, le modèle hésite comme s'il avait 50 mots également plausibles à chaque position. Donc :
- **Plus la perplexité est basse, mieux c'est** : le modèle est "confiant" et attribue de fortes probabilités aux bons mots.
- PPL = 1 serait parfait (le modèle prédit toujours le bon mot avec certitude).
- Une PPL très élevée (centaines, milliers) indique un modèle médiocre.

**Pourquoi "intrinsèque" ?** Parce que ça mesure la qualité du modèle sur un corpus de test, sans le comparer à une autre sortie. C'est une métrique de **modélisation du langage** au sens strict.

**Limites :** PPL faible ne garantit pas que le modèle produit du texte utile, factuel ou aligné avec l'intention humaine. Un modèle peut avoir une excellente perplexité et générer du texte fluide mais sans intérêt.

---

## En résumé : quand utiliser laquelle ?

| Métrique | Tâche | Type | Comparaison |
|----------|-------|------|-------------|
| **BLEU** | Traduction | Précision sur n-grammes | Avec référence |
| **ROUGE** | Résumé | Recall sur n-grammes | Avec référence |
| **Perplexité** | Modèles de langage | Probabiliste, intrinsèque | Sans référence |

Aujourd'hui, ces métriques restent largement utilisées mais sont souvent complétées par des métriques plus modernes basées sur des embeddings sémantiques (BERTScore, BLEURT) ou par des évaluations LLM-as-a-judge, parce qu'elles capturent mieux le sens que les simples correspondances lexicales.