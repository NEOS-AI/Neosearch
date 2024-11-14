--
-- 한국어 hunspell 사전의 경우 아래 링크에서 다운가능:
-- <https://github.com/spellcheck-ko/hunspell-dict-ko>
--
-- 깃허브에서 설명을 참고해서 affix 파일과 dict 파일을 다운 및 cp 하면 됨.
--
-- 참고: <https://postgresql.kr/blog/hunspell_postgresql.html>
--

-- korean_hunspell dictionary 생성
CREATE TEXT SEARCH DICTIONARY korean_hunspell (
    TEMPLATE = ispell,
    DictFile = hunspell_korean,
    AffFile = hunspell_korean
);

-- 구문 분석 config 생성
CREATE TEXT SEARCH CONFIGURATION korean_hunspell (copy=english);

ALTER TEXT SEARCH CONFIGURATION korean_hunspell alter mapping for word with korean_hunspell, simple;

-- 생성된 conifg 확인
\dF+ korean_hunspell

-- 파이썬 unicodedata 모듈 기반의 자음/모음 분리 모듈 추가
CREATE EXTENSION plpython3u;
CREATE OR REPLACE FUNCTION public.to_nfd(s text)
    RETURNS text
    LANGUAGE plpython3u
    IMMUTABLE PARALLEL SAFE
AS $function$
import unicodedata
return unicodedata.normalize('NFD', s)
$function$;

-- 테스트
select * from ts_debug('korean_hunspell', '무궁화 꽃이 피었습니다');
