---
title: Global Hiking Explorer
title_zh: 全球徒步探索器
year: 2026
period: 2026
status: ongoing
category: Ongoing
order: 2
summary: TerraPulse — a bilingual 4D spatiotemporal GIS explorer of iconic hiking trails worldwide: 3D terrain globes, satellite remote sensing, seasonal climate windows and live GIS analytics across ten routes on six continents.
summary_zh: 一款双语 4D 时空 GIS 世界经典徒步路线探索器：3D 地形、卫星遥感、季节气候窗口与实时地理分析，覆盖六大洲十条经典步道。
image: project-hiking
link: https://jianghao.wang/global-hiking-explorer/
tags: gis, mapping, hiking, threejs, maplibre, bilingual
---

TerraPulse is a bilingual (English ⇄ 中文) multi-page interactive atlas of the
world's iconic hiking trails — a 4D spatiotemporal GIS explorer that couples 3D
terrain, satellite remote sensing, seasonal climate windows and live GIS
analytics. Ten routes across six continents, all driven by one shared data model.

## Six pages, one data model

- **Home** — an immersive landing with a 3D globe, a season spotlight and curated collections
- **World Atlas** — a digital-earth "beacon" explorer
- **Trail Library** — search, filter and sort across every route
- **Trail Dossier** — a full bilingual dossier per route (terrain, climate, hazards, logistics)
- **4D Analytics** — heatmaps, scatter plots, league tables and a climate "face-off"
- **Field Notes** — method, data sources, glossary and credits

## Highlights

- **True bilingual switching** — route names, stories, hazards and every interface
  label follow the visitor's language, persisted between visits.
- **A live terrain console in every dossier** — MapLibre GL renders real
  hillshaded terrain with the route as a glowing corridor, clickable waypoints,
  a DEM toggle and a "Fly Along" mode.
- **Custom canvas visualizations** — elevation profiles, climate curves and 4D
  heatmaps drawn from scratch, no charting library.

## Tech

MapLibre GL JS · Three.js · Canvas · OpenStreetMap · Esri World Imagery ·
AWS/Copernicus DEM terrain tiles — every layer open and public, with a graceful
fallback when tile servers are unreachable.
