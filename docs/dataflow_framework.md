# Dataflow Framework

Forward:

```text
IN[n]  = MEET(OUT[p])
OUT[n] = F_n(IN[n])
```

Backward:

```text
OUT[n] = MEET(IN[s])
IN[n]  = F_n(OUT[n])
```

Live Variable Analysis:

```text
OUT[n] = union(IN[s])
IN[n]  = USE[n] union (OUT[n] - DEF[n])
```
