"""Host-compiled regression coverage for mask-aware palette Scale2x."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_mask_aware_scale2x_kernel_contract(tmp_path: Path) -> None:
    source = tmp_path / "scale2x_mask_fixture.c"
    binary = tmp_path / "scale2x_mask_fixture"
    source.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_scale2x_core.h"

static void legacy(const uint8_t *s, unsigned w, unsigned h, uint8_t *d) {
    unsigned x, y;
    for (y = 0; y < h; ++y) for (x = 0; x < w; ++x) {
        unsigned xm = x ? x - 1 : x, xp = x + 1 < w ? x + 1 : x;
        unsigned ym = y ? y - 1 : y, yp = y + 1 < h ? y + 1 : y;
        uint8_t e=s[y*w+x], b=s[ym*w+x], l=s[y*w+xm], r=s[y*w+xp], bot=s[yp*w+x];
        uint8_t p[4]={e,e,e,e};
        if (b != bot && l != r) {
            p[0] = l == b ? l : e; p[1] = b == r ? r : e;
            p[2] = l == bot ? l : e; p[3] = bot == r ? r : e;
        }
        d[(2*y)*(2*w)+2*x]=p[0]; d[(2*y)*(2*w)+2*x+1]=p[1];
        d[(2*y+1)*(2*w)+2*x]=p[2]; d[(2*y+1)*(2*w)+2*x+1]=p[3];
    }
}

int main(void) {
    uint8_t diamond[25], mask[25], output[100], fully[9]={0,1,0,1,7,1,0,1,0};
    uint8_t all[9], expected[36], actual[36];
    uint8_t counter[9]={7,0,7,0,7,7,7,7,7};
    uint8_t counter_mask[9]={0,0,0,0,1,0,0,0,0};
    uint8_t zero_neighbor[9]={8,0,8,0,7,7,8,7,8};
    uint8_t zero_mask[9]={1,1,1,1,1,1,1,1,1};
    uint8_t a[12]={0,0,0,0,0,7,7,0,0,7,0,0};
    uint8_t b[12]={255,255,255,255,255,7,7,255,255,7,255,255};
    uint8_t replay_mask[6], sample[9], sample_mask[9], sample_out[36];
    unsigned i, x, y, pattern;

    memset(diamond, 7, sizeof(diamond)); memset(mask, 0, sizeof(mask));
    /* RLE-like diamond: each row's written span grows by one then shrinks. */
    for (y=0; y<5; ++y) for (x=0; x<5; ++x)
        if (x >= (y < 2 ? 2-y : y-2) && x < 5-(y < 2 ? 2-y : y-2)) mask[y*5+x]=1;
    assert(g1_scale2x_build_masked(diamond,5,mask,5,5,5,output,10));
    for (y=0; y<5; ++y) for (x=0; x<5; ++x) if(mask[y*5+x]) {
        for(i=0;i<4;++i) assert(output[(2*y+i/2)*10+2*x+i%2] == 7);
    }

    /* Lap902 counterexample: unwritten zero neighbors behave as center E. */
    assert(g1_scale2x_build_masked(counter,3,counter_mask,3,3,3,actual,6));
    assert(actual[14]==7 && actual[15]==7 && actual[20]==7 && actual[21]==7);
    memset(counter_mask,1,sizeof(counter_mask));
    assert(g1_scale2x_build_masked(counter,3,counter_mask,3,3,3,actual,6));
    assert(actual[14]==0 && actual[15]==7 && actual[20]==7 && actual[21]==7);

    /* Fully-written frames preserve legacy byte output. */
    for(i=0;i<9;++i) all[i]=fully[i];
    memset(mask,1,sizeof(all)); legacy(all,3,3,expected);
    assert(g1_scale2x_build_masked(all,3,mask,3,3,3,actual,6));
    assert(memcmp(expected,actual,sizeof(expected))==0);

    /* A writer-produced palette zero remains a real color and can be selected. */
    assert(g1_scale2x_build_masked(zero_neighbor,3,zero_mask,3,3,3,actual,6));
    assert(actual[14]==0);

    /* Every 3x3 write-mask shape obeys the source-value and two-change bounds. */
    for(pattern=0;pattern<512;++pattern) {
        for(i=0;i<9;++i) {
            sample_mask[i]=(pattern>>i)&1u;
            sample[i]=(uint8_t)(((pattern*(i+3u)+i*5u)%3u)==0u ? 0u :
                                (((pattern+i*7u)%2u)==0u ? 7u : 11u));
        }
        assert(g1_scale2x_build_masked(sample,3,sample_mask,3,3,3,sample_out,6));
        for(y=0;y<3;++y) for(x=0;x<3;++x) if(sample_mask[y*3+x]) {
            unsigned xm=x?x-1:x, xp=x<2?x+1:x, ym=y?y-1:y, yp=y<2?y+1:y;
            unsigned neighbors[5]={y*3+x,ym*3+x,y*3+xm,y*3+xp,yp*3+x};
            uint8_t e=sample[y*3+x]; unsigned changed=0, q;
            unsigned offsets[4]={(2*y)*6+2*x,(2*y)*6+2*x+1,
                                 (2*y+1)*6+2*x,(2*y+1)*6+2*x+1};
            for(q=0;q<4;++q) {
                uint8_t value=sample_out[offsets[q]]; unsigned n, found=0;
                if(value!=e) ++changed;
                for(n=0;n<5;++n) if((n==0 || sample_mask[neighbors[n]]) &&
                                      sample[neighbors[n]]==value) found=1;
                assert(found);
            }
            assert(changed<=2);
        }
    }

    /* Clip identity mask is the equality of 0x00 / 0xFF replays. */
    for(i=0;i<6;++i) replay_mask[i]=(a[i]==b[i]);
    assert(replay_mask[0]==0 && replay_mask[5]==1);
    return 0;
}
''',
        encoding="utf-8",
    )
    result = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I",
         str(ROOT / "tools/inmm_stub"), str(source), "-o", str(binary)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = subprocess.run([str(binary)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
