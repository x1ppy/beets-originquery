beets-originquery
=================

Plugin for beets that uses supplemental files in imported directories to improve MusicBrainz matches for untagged data.

Motivation
----------

Whenever beets tries to identify your music, it queries MusicBrainz using tags from your music files.  The query returns
only the few best matches of the many possible results, however, so the better your tags, the more likely you are to get
a good match.

But one of the reasons we're using beets to begin with is to _get_ those tags; music is often tagged with only the most
essential data (i.e., album and artist), lacking tags that could actually identify the specific edition of an album.
That puts us in a chicken-and-egg situation: beets can't accurately identify the release until it has relevant tags, but
it can't assign relevant tags without knowing the release!

In other words, while beets is an excellent tool, it's only as useful as the data it has available. It's common to store
extra data in separate text or JSON files, but that data isn't read by beets as it's not included in music files
themselves. If only there were a way to feed this origin data to beets to supplement our tags to accurately identify
editions…

Enter `originquery`.

Installation
------------

This plugin relies on cutting-edge beets features to work. In particular, your beets installation must support the 
[`extra_tags`](https://github.com/beetbox/beets/blob/master/docs/reference/config.rst#id70) setting, which is not yet in
an official beets release. Until beets v1.5.0 is released with [the commit adding this
feature](https://github.com/beetbox/beets/commit/8ed76f1198c23b9205c6f566860a35569945d4bb), you must install the latest
beets manually:

    $> pip install git+https://github.com/beetbox/beets
    $> beet --version
    beets version 1.5.0

Once you have the latest and greatest beets, you can install this plugin:

    $> pip install git+https://github.com/x1ppy/beets-originquery

Next, add the following section to your beets config file to enable improved MediaBrainz queries from tags:

    musicbrainz:
        extra_tags: [year, catalognum, country, media, label]

Finally, add `originquery` to the `plugins` section of your beets config file, creating it if it doesn't exist:

    plugins:
        - originquery

Configuration
-------------

`originquery` reads an _origin file_ at the root of each album directory when music is imported. The origin file can be
either a text or JSON file. Beyond that, the format of the file is entirely user-defined and is specified in the
`originquery` configuration.

Your beets configuration must contain a section with the following fields:

    originquery:
        origin_file: <origin_file_name>
        tag_patterns:
            <tag1>: <pattern1>
            <tag2>: <pattern2>

The `origin_file` supports glob wildcard characters. So, for instance, if you use a date scheme for your origin file
naming (e.g., `origin-2020025.txt`), you could specify `origin_file: 'origin-*.txt'` here. If the pattern matches
multiple files, the first file in the alphanumerically sorted list of results will be used.

The tags under `tag_patterns` can be any combination of the following tags:
* `media` (CD, vinyl, …)
* `year` (edition year, _not_ original release year)
* `country` (US, Japan, …)
* `label` (Epic, Atlantic, …)
* `catalognum` (ABC-XYZ, 102030, …)
* `albumdisambig` (Remastered, Deluxe Edition, …)

The patterns used will depend on whether your origin file is a text file or JSON file, as outlined below.

### Text files

When using text origin files, the `tag_patterns` pattern must be a regular expression containing a single match group
corresponding to the value for the given tag.

As an arbitrary example, you might have origin files that look like the following:

    media=CD
    year=1988
    label=Mobile Fidelity Sound Lab
    catalognum=UDCD 517

In this case, your beets config would look like this:

    originquery:
        origin_file: origin.txt
        tag_patterns:
            media: 'media=(.+)'
            year: 'year=(\d{4})'
            label: 'label=(.+)'
            catalognum: 'catalognum=(.+)'

This means that you have a file named `origin.txt` at the root of each album directory, and the `media`, `year`, `label`,
and `catalognum` tags will be parsed from this file and used by beets to query MusicBrainz. In this case, each tag and
value would be listed in the origin file separated by an `=` (i.e., `<tag>=<value>`) as shown in the example. Of course,
you're free to use a completely different formatting scheme if you update the patterns accordingly.

### JSON files

With JSON origin files, the `tag_patterns` pattern must be a [JSONPath](https://goessner.net/articles/JsonPath/)
expression that points to the value for the given tag.

As an arbitrary example, you might have origin files that look like the following:

    {
      "mydata": {
        "media": "CD",
        "year": 1988,
        "label": "Mobile Fidelity Sound Lab",
        "catalognum": "UDCD 517"
      }
    }

In this case, your beets config would look like this:

    originquery:
        origin_file: origin.json
        tag_patterns:
            media: '$.mydata.media'
            year: '$.mydata.year'
            label: '$.mydata.label'
            catalognum: '$.mydata.catalognum'

This means that you have a file named `origin.json` at the root of each album directory, and the `media`, `year`, `label`,
and `catalognum` tags will be parsed from this file and used by beets to query MusicBrainz. In this case, the tag and
value mappings would be defined in an object literal under the `mydata` key at the root of the object as shown in the
example. Of course, you're free to use a completely different schema if you update the patterns accordingly.

Examples
-----

### Before `originquery`

Just as a baseline, let's first try a beets import without `originquery`. We'll import [this
edition](https://musicbrainz.org/release/51a4e8b4-1af1-4daf-a746-ac1c7206dd02) of Led Zeppelin's Houses of the Holy:

    $> beet import ~/music

    /home/x1ppy/music/(1973) Houses Of The Holy [2014 Remaster] (8 items)
    Correcting tags from:
        Led Zeppelin - Houses Of The Holy
    To:
        Led Zeppelin - Houses of the Holy
    URL:
        https://musicbrainz.org/release/3ccb4cb2-940a-4e2e-b1fd-4c0b7483280f
    (Similarity: 100.0%) (12" Vinyl, 1973, US, Atlantic, SD 7255)
     * The Song Remains The Same   -> The Song Remains the Same
     * Over The Hills And Far Away -> Over the Hills and Far Away
     * D'yer Mak'er                -> D’yer Mak’er
    [A]pply, More candidates, Skip, Use as-is, as Tracks, Group albums, Enter search, enter Id, aBort?

Nice, 100%! A perfect match…or is it?

On closer inspection, you'll notice that this is actually a very different edition than the one we're importing. beets
is reporting the media as 12" Vinyl (instead of CD), the edition year is 1973 (instead of 2014), and the catalog number
is different. No bueno.

### With `originquery`

Now, let's compare that to a query with `originquery` enabled:

    $> beet import ~/music

    /home/x1ppy/music/(1973) Houses Of The Holy [2014 Remaster] (8 items)
    originquery: Using origin file /home/x1ppy/music/(1973) Houses Of The Holy [2014 Remaster]/origin.txt
    originquery: ╔════════════════╤═════════════╤═════════════╗
    originquery: ║ Field          │ Tagged Data │ Origin Data ║
    originquery: ╟────────────────┼─────────────┼─────────────╢
    originquery: ║ Media          │             │ CD          ║
    originquery: ║ Edition year   │ 1973        │ 2014        ║
    originquery: ║ Record label   │             │ Atlantic    ║
    originquery: ║ Catalog number │             │ 8122795828  ║
    originquery: ║ Edition        │             │ Remastered  ║
    originquery: ╚════════════════╧═════════════╧═════════════╝
    Correcting tags from:
        Led Zeppelin - Houses Of The Holy
    To:
        Led Zeppelin - Houses of the Holy
    URL:
        https://musicbrainz.org/release/51a4e8b4-1af1-4daf-a746-ac1c7206dd02
    (Similarity: 100.0%) (CD, 2014, XE, Atlantic, 8122795828)
     * The Song Remains The Same   -> The Song Remains the Same
     * Over The Hills And Far Away -> Over the Hills and Far Away
     * D'yer Mak'er                -> D’yer Mak’er
    [A]pply, More candidates, Skip, Use as-is, as Tracks, Group albums, Enter search, enter Id, aBort?

Another 100% match! This time, though, all of the fields reported by beets exactly match the ones we were looking for.
Success!

You'll also notice the shiny new table shown with the beets result. This gives us a handy reference for tags: the Tagged
Data column lists the data beets found in the music files, and the Origin Data column lists the data `originquery`
pulled from the origin file. With this information on hand, it's now clear why beets wasn't able to match the proper
edition: the music tags don't contain _any_ tags that could actually identify the specific release!

### Conflicts

Occasionally, you might see `originquery` complain about conflicts between tagged data and origin data:

    /home/x1ppy/music/Billy Joel - 1978 - 52nd Street (9 items)
    originquery: Using origin file /home/x1ppy/music/Billy Joel - 1978 - 52nd Street/origin.txt
    originquery: ╔════════════════╤═════════════╤════════════════╗
    originquery: ║ Field          │ Tagged Data │ Origin Data    ║
    originquery: ╟────────────────┼─────────────┼────────────────╢
    originquery: ║ Media          │             │ CD             ║
    originquery: ║ Edition year   │ 1978        │ 2010           ║
    originquery: ║ Record label   │ Columbia    │ Audio Fidelity ║
    originquery: ║ Catalog number │ IDK 35609   │ AFZ 095        ║
    originquery: ╚════════════════╧═════════════╧════════════════╝
    originquery: Origin data conflicts with tagged data.
    Tagging:
        Billy Joel - 52nd Street
    URL:
        https://musicbrainz.org/release/6942718c-2fd2-4227-a882-130c500806f5
    (Similarity: 100.0%) (CD, 1978, CA, Columbia, IDK 35609)
    [A]pply, More candidates, Skip, Use as-is, as Tracks, Group albums, Enter search, enter Id, aBort?

This happens if either the music is mistagged or the origin file contains the wrong origin data. Here, we see the tagged
catalog number is `IDK 35609`, but the origin data is `AFZ 095`. These are clearly different editions, and it wouldn't
make sense to try to merge them to search MusicBrainz, so `originquery` chooses just one set of values to query
MusicBrainz and ignores the other.

By default, `originquery` uses the _tagged data_ in the case of a conflict. This behavior can be changed by setting
`use_origin_on_conflict` to `yes` in the beets config:

    originquery:
        ...
        use_origin_on_conflict: yes

Changelog
---------
### [1.0.1] - 2020-03-25
* Added support for glob patterns in `origin_file`
### [1.0.0] - 2020-03-23
* Initial release

[1.0.1]: https://github.com/x1ppy/beets-originquery/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/x1ppy/beets-originquery/releases/tag/1.0.0
