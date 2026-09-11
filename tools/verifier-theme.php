<?php
/**
 * Exécute chaque gabarit du thème avec un WordPress simulé.
 *
 *     php tools/verifier-theme.php
 *
 * Pourquoi : `php -l` ne contrôle que la syntaxe. Il a validé sans broncher un
 * `esc_html__( "…%1$s…" )` — entre guillemets doubles, PHP interprète `$s`
 * comme une variable, le format devient `%1`, et printf lève une ValueError.
 * Résultat en production : « Il y a eu une erreur critique sur ce site. »
 *
 * Ce script charge les gabarits pour de vrai, avec des doublures des fonctions
 * WordPress utilisées. Toute erreur d'exécution — format invalide, argument
 * manquant, fonction inconnue — remonte ici au lieu du site du client.
 *
 * Ce n'est pas un test unitaire : on ne vérifie pas ce qui est rendu, on
 * vérifie que ça ne casse pas.
 */

declare( strict_types = 1 );

// Le thème à vérifier : premier argument, ou allodj-theme par défaut.
$demande = $argv[1] ?? '../allodj-theme';
$theme   = realpath( $demande ) ?: realpath( dirname( __DIR__, 1 ) . '/' . $demande );

if ( ! $theme || ! is_dir( $theme ) ) {
	fwrite( STDERR, "Thème introuvable : {$theme}\n" );
	exit( 1 );
}

// Toute notice ou avertissement devient une exception : un « undefined variable »
// silencieux est précisément ce qui a produit le bug.
set_error_handler(
	static function ( int $niveau, string $message, string $fichier, int $ligne ): bool {
		throw new ErrorException( $message, 0, $niveau, $fichier, $ligne );
	}
);

define( 'ABSPATH', $theme . '/' );

// ── Doublures WordPress ────────────────────────────────────────────────────
function __( $t, $d = '' ) { return $t; }
function _x( $t, $c = '', $d = '' ) { return $t; }
function _n( $s, $p, $n, $d = '' ) { return 1 === $n ? $s : $p; }
function esc_html( $t ) { return htmlspecialchars( (string) $t, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $t ) { return esc_html( $t ); }
function esc_url( $u ) { return (string) $u; }
function esc_url_raw( $u ) { return (string) $u; }
function esc_html__( $t, $d = '' ) { return esc_html( $t ); }
function esc_attr__( $t, $d = '' ) { return esc_html( $t ); }
function esc_html_e( $t, $d = '' ) { echo esc_html( $t ); }
function esc_attr_e( $t, $d = '' ) { echo esc_html( $t ); }
function wp_kses( $t, $a ) { return $t; }
function wp_kses_post( $t ) { return $t; }
function wp_strip_all_tags( $t ) { return strip_tags( (string) $t ); }
function sanitize_text_field( $t ) { return (string) $t; }
function wp_parse_args( $a, $d = array() ) { return array_merge( $d, (array) $a ); }
function apply_filters( $h, $v, ...$r ) { return $v; }
function add_action( ...$a ) {}
function add_filter( ...$a ) {}
function home_url( $p = '/' ) { return 'https://exemple.test' . $p; }
function get_bloginfo( $c = '' ) { return 'AlloDJ'; }
function get_template_directory() { global $theme_dir; return $theme_dir; }
function get_template_directory_uri() { return 'https://exemple.test/wp-content/themes/allodj'; }
function get_theme_mod( $k, $d = false ) { return $d; }
function has_custom_logo() { return false; }
function has_site_icon() { return false; }
function has_nav_menu( $l ) { return false; }
function is_front_page() { return true; }
function wp_json_encode( $d, $f = 0 ) { return json_encode( $d, $f ); }
function wp_date( $f ) { return date( $f ); }
function get_query_var( $v ) { return ''; }
function current_user_can( $c ) { return false; }
function wp_get_attachment_image( ...$a ) { return ''; }
function add_rewrite_rule( ...$a ) {}
function flush_rewrite_rules() {}
function wp_enqueue_style( ...$a ) {}
function wp_enqueue_script( ...$a ) {}
function wp_localize_script( ...$a ) {}
function load_theme_textdomain( ...$a ) {}
function add_theme_support( ...$a ) {}
function register_nav_menus( ...$a ) {}
function wp_nav_menu( ...$a ) {}
// Pages légales simulées : sans elles, le repli du pied de page ne serait
// jamais exécuté et le test ne prouverait rien.
function get_page_by_path( $chemin ) {
	$connus = array( 'cgu', 'confidentialite', 'mentions-legales', 'suppression-de-compte', 'support' );
	if ( ! in_array( $chemin, $connus, true ) ) {
		return null;
	}
	return (object) array( 'post_status' => 'publish', 'post_name' => $chemin );
}
function get_permalink( $p = null ) { return 'https://exemple.test/' . ( is_object( $p ) ? $p->post_name : 'page' ) . '/'; }
function get_the_title( $p = null ) { return is_object( $p ) ? ucfirst( str_replace( '-', ' ', $p->post_name ) ) : 'Titre'; }
function get_the_modified_date( $f ) { return date( $f ); }
function have_posts() { return false; }
function the_post() {}
function the_title() { echo 'Titre'; }
function the_content() { echo '<p>Contenu</p>'; }
function wp_script_is( ...$a ) { return false; }
function get_header() {}
function get_footer() {}
function wp_footer() {}
function wp_head() {}
function wp_body_open() {}
function body_class( ...$a ) {}
function language_attributes() {}
function bloginfo( $c = '' ) { echo 'AlloDJ'; }
function user_trailingslashit( $s, $t = '' ) { return rtrim( $s, '/' ) . '/'; }
function wp_unslash( $v ) { return $v; }
function wp_parse_url( $u, $c = -1 ) { return parse_url( $u, $c ); }
function remove_filter( ...$a ) {}
function get_locale() { return 'fr_FR'; }
function untrailingslashit( $s ) { return rtrim( $s, '/' ); }
function trailingslashit( $s ) { return rtrim( $s, '/' ) . '/'; }
function get_option( $k, $d = false ) { return 'https://exemple.test'; }
function add_query_arg( $k, $v, $url ) { return $url . ( strpos( $url, '?' ) === false ? '?' : '&' ) . $k . '=' . $v; }
$_SERVER['REQUEST_URI'] = $_SERVER['REQUEST_URI'] ?? '/';

global $theme_dir;
$theme_dir = $theme;

// ── Chargement du thème ────────────────────────────────────────────────────
require $theme . '/inc/faq.php';
require $theme . '/inc/seo.php';
require $theme . '/inc/i18n.php';

// functions.php enregistre des hooks ; on ne prend que les fonctions utilitaires.
$fonctions = file_get_contents( $theme . '/functions.php' );
$fonctions = preg_replace( '/^\s*require_once .*$/m', '', $fonctions );
// exit() sur ABSPATH absent : inutile ici, et define() en double sinon.
$fonctions = preg_replace( '/if \( ! defined\( .ABSPATH. \) \) \{\s*exit;\s*\}/', '', $fonctions );
$fonctions = preg_replace( '/^\s*(add_action|add_filter)\(.*$/m', '', $fonctions );
$fonctions = str_replace( '<?php', '', $fonctions );
eval( $fonctions ); // phpcs:ignore Squiz.PHP.Eval -- outil de développement local.

// ── Exécution de chaque gabarit ────────────────────────────────────────────
$gabarits = glob( $theme . '/template-parts/*.php' );
$echecs   = 0;

foreach ( $gabarits as $g ) {
	$nom = basename( $g );
	ob_start();
	try {
		include $g;
		$sortie = ob_get_clean();
		$octets = strlen( $sortie );
		printf( "  ok       %-24s %6d octets rendus\n", $nom, $octets );
	} catch ( Throwable $e ) {
		ob_end_clean();
		++$echecs;
		printf( "  ECHEC    %-24s %s\n", $nom, $e->getMessage() );
		printf( "           %s:%d\n", basename( $e->getFile() ), $e->getLine() );
	}
}

// ── Le pied de page et le gabarit légal, hors boucle template-parts ────────
foreach ( array( 'footer.php', 'page-legal.php' ) as $g ) {
	ob_start();
	try {
		include $theme . '/' . $g;
		$sortie = ob_get_clean();
		printf( "  ok       %-24s %6d octets rendus
", $g, strlen( $sortie ) );
	} catch ( Throwable $e ) {
		ob_end_clean();
		++$echecs;
		printf( "  ECHEC    %-24s %s
", $g, $e->getMessage() );
		printf( "           %s:%d
", basename( $e->getFile() ), $e->getLine() );
	}
}

// ── Les fonctions qui construisent du texte formaté ────────────────────────
foreach ( array( 'allodj_description', 'allodj_faq', 'allodj_liens_legaux', 'allodj_lang', 'allodj_is_en', 'allodj_current_path_fr' ) as $f ) {
	try {
		$r = $f();
		$taille = is_array( $r ) ? count( $r ) . ' entrées' : strlen( (string) $r ) . ' octets';
		printf( "  ok       %-24s %s\n", $f . '()', $taille );
	} catch ( Throwable $e ) {
		++$echecs;
		printf( "  ECHEC    %-24s %s\n", $f . '()', $e->getMessage() );
	}
}

echo "\n";
if ( $echecs ) {
	printf( "%d gabarit(s) en échec — NE PAS LIVRER.\n", $echecs );
	exit( 1 );
}
printf( "%d gabarits exécutés sans erreur.\n", count( $gabarits ) );
