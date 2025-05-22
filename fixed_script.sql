CREATE TYPE "public"."language" AS ENUM('cs', 'en', 'de');
CREATE TYPE "public"."registration_status" AS ENUM('pending', 'confirmed', 'cancelled', 'rejected');
CREATE TYPE "public"."token_transaction_type" AS ENUM('purchase', 'reward', 'donation', 'payment', 'refund');
CREATE TYPE "public"."tournament_format" AS ENUM('knockout', 'groups', 'round_robin', 'swiss', 'league', 'custom');
CREATE TYPE "public"."tournament_status" AS ENUM('created', 'registration_open', 'registration_closed', 'in_progress', 'completed', 'cancelled');
CREATE TABLE "matches" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tournament_id" integer NOT NULL,
	"phase_id" uuid,
	"round_number" smallint,
	"match_number" smallint,
	"next_match_id" uuid,
	"player1_id" uuid,
	"player2_id" uuid,
	"winner" uuid,
	"completed" boolean DEFAULT false,
	"scheduled_time" timestamp,
	"result" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "organizers" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" varchar(255) NOT NULL,
	"description" text,
	"logo" text,
	"user_id" uuid,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "registrations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tournament_id" integer NOT NULL,
	"user_id" uuid NOT NULL,
	"status" "registration_status" DEFAULT 'pending' NOT NULL,
	"payment_completed" boolean DEFAULT false,
	"payment_method" varchar(50),
	"registration_date" timestamp DEFAULT now() NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "sport_translations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sport_id" varchar(10) NOT NULL,
	"language" "language" NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "sports" (
	"id" varchar(10) PRIMARY KEY NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "token_transactions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"from_wallet_id" uuid,
	"to_wallet_id" uuid,
	"amount" integer NOT NULL,
	"type" "token_transaction_type" NOT NULL,
	"description" text,
	"tournament_id" integer,
	"match_id" uuid,
	"created_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "token_wallets" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"balance" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "token_wallets_user_id_unique" UNIQUE("user_id")
);

CREATE TABLE "tournament_phases" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tournament_id" integer NOT NULL,
	"name" varchar(100) NOT NULL,
	"order" smallint NOT NULL,
	"start_date" timestamp,
	"end_date" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "tournament_translations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tournament_id" integer NOT NULL,
	"language" "language" NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "tournaments" (
	"id" integer PRIMARY KEY NOT NULL,
	"sport_id" varchar(10) NOT NULL,
	"organizer_id" uuid,
	"venue_id" uuid,
	"status" "tournament_status" DEFAULT 'created' NOT NULL,
	"format" "tournament_format" DEFAULT 'knockout' NOT NULL,
	"capacity" smallint NOT NULL,
	"start_date" timestamp NOT NULL,
	"end_date" timestamp NOT NULL,
	"registration_start_date" timestamp,
	"registration_end_date" timestamp,
	"price" integer DEFAULT 0,
	"allow_tokens" boolean DEFAULT false,
	"token_price" integer DEFAULT 0,
	"custom_rules" text,
	"banner_image" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "users" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"email" varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	"avatar" text,
	"preferred_language" "language" DEFAULT 'en',
	"is_organizer" boolean DEFAULT false,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "users_email_unique" UNIQUE("email")
);

CREATE TABLE "venues" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" varchar(255) NOT NULL,
	"address" text NOT NULL,
	"city" varchar(100) NOT NULL,
	"country" varchar(100) NOT NULL,
	"latitude" text,
	"longitude" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

ALTER TABLE "matches" ADD CONSTRAINT "matches_tournament_id_tournaments_id_fk" FOREIGN KEY ("tournament_id") REFERENCES "public"."tournaments"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "matches" ADD CONSTRAINT "matches_phase_id_tournament_phases_id_fk" FOREIGN KEY ("phase_id") REFERENCES "public"."tournament_phases"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "matches" ADD CONSTRAINT "matches_player1_id_users_id_fk" FOREIGN KEY ("player1_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "matches" ADD CONSTRAINT "matches_player2_id_users_id_fk" FOREIGN KEY ("player2_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "matches" ADD CONSTRAINT "matches_winner_users_id_fk" FOREIGN KEY ("winner") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "organizers" ADD CONSTRAINT "organizers_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "registrations" ADD CONSTRAINT "registrations_tournament_id_tournaments_id_fk" FOREIGN KEY ("tournament_id") REFERENCES "public"."tournaments"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "registrations" ADD CONSTRAINT "registrations_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "sport_translations" ADD CONSTRAINT "sport_translations_sport_id_sports_id_fk" FOREIGN KEY ("sport_id") REFERENCES "public"."sports"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "token_transactions" ADD CONSTRAINT "token_transactions_from_wallet_id_token_wallets_id_fk" FOREIGN KEY ("from_wallet_id") REFERENCES "public"."token_wallets"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "token_transactions" ADD CONSTRAINT "token_transactions_to_wallet_id_token_wallets_id_fk" FOREIGN KEY ("to_wallet_id") REFERENCES "public"."token_wallets"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "token_transactions" ADD CONSTRAINT "token_transactions_tournament_id_tournaments_id_fk" FOREIGN KEY ("tournament_id") REFERENCES "public"."tournaments"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "token_transactions" ADD CONSTRAINT "token_transactions_match_id_matches_id_fk" FOREIGN KEY ("match_id") REFERENCES "public"."matches"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "token_wallets" ADD CONSTRAINT "token_wallets_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "tournament_phases" ADD CONSTRAINT "tournament_phases_tournament_id_tournaments_id_fk" FOREIGN KEY ("tournament_id") REFERENCES "public"."tournaments"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "tournament_translations" ADD CONSTRAINT "tournament_translations_tournament_id_tournaments_id_fk" FOREIGN KEY ("tournament_id") REFERENCES "public"."tournaments"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "tournaments" ADD CONSTRAINT "tournaments_sport_id_sports_id_fk" FOREIGN KEY ("sport_id") REFERENCES "public"."sports"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "tournaments" ADD CONSTRAINT "tournaments_organizer_id_organizers_id_fk" FOREIGN KEY ("organizer_id") REFERENCES "public"."organizers"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "tournaments" ADD CONSTRAINT "tournaments_venue_id_venues_id_fk" FOREIGN KEY ("venue_id") REFERENCES "public"."venues"("id") ON DELETE no action ON UPDATE no action;