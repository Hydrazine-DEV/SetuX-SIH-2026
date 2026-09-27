# AI Verification Pipeline

SetuX incorporates a multi-tiered inspection pipeline to audit incoming evidence:

## Pipeline Stages

```
[Evidence Submission] 
       │
       ▼
[Metadata Audit] ──────► Timestamp & Image Hash Deduplication check
       │
       ▼
[GPS Proximity] ──────► Haversine geofence check (registered vs current GPS)
       │
       ▼
[CV Progress Engine] ──► Segmentation network & edge detection for layers
       │
       ▼
[Anomaly Score] ──────► Multi-tiered scoring logic (discrepancy + flags)
       │
       ▼
[Final Decision] ─────► Approved OR Supervisor Review OR Manual Inspection
```

### Future Computer Vision Integration
In production, the **CV Progress Engine** should be swapped with a segmentation model (e.g. YOLOv8-seg or Mask R-CNN) trained on construction site components to calculate percentage completeness of specific elements.
