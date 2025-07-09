import diff_match_patch


def get_diff(original: str, result: str) -> str:
    dmp = diff_match_patch.diff_match_patch()
    diffs = dmp.diff_main(original, result)
    dmp.diff_cleanupSemantic(diffs)
    # Return as HTML for frontend diff viewer
    return dmp.diff_prettyHtml(diffs) 