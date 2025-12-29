# PodEdit Project File Structure

Generated on: 2025-12-08

```
podedit/
│
├── .venv/                              # Python virtual environment
│
├── DATASET_COLLECTION_GUIDE.md         # Guide for collecting datasets (1.1 KB)
├── RESEARCH_PLAN.md                    # Research plan document (563 B)
│
├── src/                                # Source code directory
│   ├── audio_processor.py              # Audio processing module (10.3 KB)
│   ├── edl_generator.py                # EDL (Edit Decision List) generation (6.6 KB)
│   ├── main.py                         # Main application entry point (7.3 KB)
│   ├── metrics_collector.py            # Metrics collection module (8.0 KB)
│   ├── silence_detector.py             # Silence detection algorithm (9.8 KB)
│   ├── speaker_detector.py             # Speaker detection module (8.6 KB)
│   ├── sync_engine.py                  # Synchronization engine (6.0 KB)
│   ├── sync_evaluation.py              # Sync evaluation utilities (1.7 KB)
│   └── timeline_merger.py              # Timeline merging logic (5.0 KB)
│
├── datasets/                           # Test datasets directory
│   ├── test_set_1/
│   │   ├── ground_truth.json           # Ground truth annotations (1.0 KB)
│   │   └── metadata.json               # Dataset metadata (30 B)
│   │
│   ├── test_set_2/
│   │   ├── ground_truth.json           # Ground truth annotations (34 B)
│   │   └── metadata.json               # Dataset metadata (30 B)
│   │
│   └── test_set_3/
│       ├── ground_truth.json           # Ground truth annotations (34 B)
│       └── metadata.json               # Dataset metadata (30 B)
│
├── evaluation/                         # Evaluation scripts and tools
│   ├── metrics.py                      # Evaluation metrics (30 B)
│   ├── statistical_tests.py            # Statistical testing module (36 B)
│   └── visualizations.py               # Visualization utilities (55 B)
│
├── results/                            # Results from different approaches
│   ├── baseline_manual_editing/
│   │   └── README.md                   # Baseline results documentation (109 B)
│   │
│   ├── commercial_tool_results/
│   │   └── README.md                   # Commercial tool results (124 B)
│   │
│   └── our_tool_results/
│       └── README.md                   # PodEdit tool results (78 B)
│
└── paper/                              # Research paper materials
    ├── draft.tex                       # LaTeX draft document (391 B)
    ├── figures/
    │   └── README.md                   # Figures directory info (61 B)
    └── tables/
        └── README.md                   # Tables directory info (59 B)
```

## Directory Overview

### `/src` - Source Code (9 files, ~58 KB)
Core implementation of the PodEdit podcast editing tool:
- **Audio Processing**: `audio_processor.py`, `silence_detector.py`, `speaker_detector.py`
- **Editing Logic**: `edl_generator.py`, `timeline_merger.py`, `sync_engine.py`
- **Evaluation**: `metrics_collector.py`, `sync_evaluation.py`
- **Main Entry**: `main.py`

### `/datasets` - Test Data (3 test sets)
Each test set contains:
- `ground_truth.json` - Manual annotations for evaluation
- `metadata.json` - Dataset information and properties

### `/evaluation` - Analysis Tools (3 files)
Scripts for evaluating tool performance:
- Metrics calculation
- Statistical significance testing
- Result visualizations

### `/results` - Experimental Results (3 subdirectories)
Comparative results from:
- Manual baseline editing
- Commercial podcast editing tools
- PodEdit (our tool)

### `/paper` - Research Paper (LaTeX)
Academic paper materials:
- Main draft in LaTeX format
- Figures and tables directories for publication assets

## File Statistics

- **Total Python files**: 12 (9 in src/ + 3 in evaluation/)
- **Total JSON files**: 6 (ground truth and metadata files)
- **Documentation files**: 7 (README.md and .md files)
- **LaTeX files**: 1 (draft.tex)
- **Total size**: ~60 KB (excluding .venv)

## Key Components

1. **Main Application**: `src/main.py` - Entry point for the PodEdit tool
2. **Core Algorithms**: Silence detection, speaker detection, and sync engine
3. **Output Format**: EDL (Edit Decision List) generation for video editors
4. **Evaluation Framework**: Comprehensive metrics and statistical testing
5. **Research Documentation**: LaTeX paper with supporting materials
