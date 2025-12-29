# Dataset Collection Protocol for Research Paper

## Minimum Required Test Cases

For statistically significant results, collect:
- **10-15 podcast episodes** with varying characteristics
- Each episode should have **2 camera angles** recorded simultaneously

## Diversity Requirements

### Audio Quality Variations
- 3 episodes: Professional studio setup (low noise)
- 3 episodes: Home recording (moderate noise)
- 3 episodes: Laptop microphones (high noise)

### Speaking Pattern Variations
- Fast-paced conversation (minimal silence)
- Interview format (turn-taking with pauses)
- Debate/overlapping speech

### Duration Variations
- Short: 5-10 minutes
- Medium: 15-30 minutes
- Long: 45-60 minutes

## Manual Annotation Process

For EACH episode, create ground_truth.json with:

1. **Sync offset**: Use audio waveform in Audacity to find exact offset
2. **Silence segments**: Mark all pauses > 2 seconds
3. **Speaker segments**: Annotate who speaks when
4. **Manual editing time**: Time yourself editing in Premiere Pro
5. **Quality ratings**: Rate final output quality (1-5 scale)
